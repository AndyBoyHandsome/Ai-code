import numpy as np
import faiss
from sklearn.cluster import DBSCAN
import pickle
import os
import insightface
import onnxruntime as ort

class FaceRecognizer:
    def __init__(self):
        self.index = None
        self.face_features = []
        self.image_ids = []
        self.quality_scores = []
        
        # 使用相对路径
        model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        self.model_path = os.path.join(model_dir, "face_model.pkl")
        
        # 根据系统选择最佳执行提供程序
        providers = ort.get_available_providers()
        if 'CoreMLExecutionProvider' in providers:
            self.providers = ['CoreMLExecutionProvider']
        else:
            self.providers = ['CPUExecutionProvider']
            
        print(f"Using providers: {self.providers}")
        
        # 初始化人脸分析模型
        self.face_analyzer = insightface.app.FaceAnalysis(
            providers=self.providers,
            allowed_modules=['detection', 'recognition']
        )
        self.face_analyzer.prepare(ctx_id=0)
        
        # 确保在M2上使用优化的CPU实现
        faiss.omp_set_num_threads(4)
        
        # 如果存在模型文件，加载现有模型
        if os.path.exists(self.model_path):
            self.load_model(self.model_path)
    
    def add_face(self, face_dict, image_id):
        """添加人脸特征向量到索引"""
        print("**添加人脸****")
        self.face_features.append(np.array(face_dict['features'], dtype=np.float32))
        self.image_ids.append(image_id)
        self.quality_scores.append(face_dict['quality_score'])
    
    def build_index(self):
        """构建Faiss索引"""
        try:
            if not self.face_features:
                print("没有人脸特征，跳过索引构建")
                return
                
            print(f"开始构建索引，特征数量: {len(self.face_features)}")
            features = np.array(self.face_features).astype('float32')
            d = features.shape[1]  # 特征维度
            print(f"特征维度: {d}")
            
            # 根据数据量选择合适的索引类型
            if len(self.face_features) < 10:
                print("使用 IndexFlatL2 索引")
                self.index = faiss.IndexFlatL2(d)
                self.index.add(features)
            else:
                print("使用 IndexIVFFlat 索引")
                nlist = min(int(len(self.face_features) / 10), 100)
                print(f"聚类中心数量: {nlist}")
                
                # 创建和训练量化器
                quantizer = faiss.IndexFlatL2(d)
                self.index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
                
                if not self.index.is_trained:
                    print("开始训练索引...")
                    try:
                        self.index.train(features)
                    except Exception as e:
                        print(f"索引训练失败: {str(e)}")
                        # 如果训练失败，回退到简单索引
                        print("回退到 IndexFlatL2 索引")
                        self.index = faiss.IndexFlatL2(d)
                
                print("添加特征到索引...")
                self.index.add(features)
            
            print("索引构建完成")
            
        except Exception as e:
            print(f"构建索引时发生错误: {str(e)}")
            # 确保即使发生错误也能继续运行
            self.index = None
    
    def cluster_faces(self, threshold=0.7):
        """使用DBSCAN聚类人脸"""
        features = np.array(self.face_features)
        quality_weights = np.array(self.quality_scores)
        
        print(f"开始计算 {len(features)} 个人脸的距离矩阵...")
        
        # 使用余弦相似度
        normalized_features = features / np.linalg.norm(features, axis=1)[:, np.newaxis]
        similarities = np.dot(normalized_features, normalized_features.T)
        
        # 确保相似度在 [0,1] 范围内
        similarities = np.clip(similarities, 0, 1)
        
        # 将相似度转换为距离
        distances = 1 - similarities  # 直接使用相似度的补值作为距离
        
        # 应用质量权重，但减小权重的影响
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                weight = np.sqrt(min(quality_weights[i], quality_weights[j]))  # 使用平方根减小权重影响
                adjusted_dist = distances[i][j] / max(weight, 0.5)  # 限制最小权重
                distances[i][j] = distances[j][i] = max(adjusted_dist, 0)
        
        print("开始DBSCAN聚类...")
        
        # 打印距离统计信息以帮助调试
        print(f"距离矩阵统计: min={distances.min():.4f}, max={distances.max():.4f}, "
              f"mean={distances.mean():.4f}, median={np.median(distances):.4f}")
        
        # 自适应确定最佳阈值
        test_thresholds = np.linspace(0.3, 0.8, 10)
        best_threshold = None
        best_num_clusters = float('inf')
        target_clusters = 8  # 目标分组数
        
        print("\n寻找最佳聚类阈值...")
        for test_threshold in test_thresholds:
            clustering = DBSCAN(
                eps=test_threshold,
                min_samples=3,  # 增加最小样本数，使分组更稳定
                metric='precomputed'
            )
            test_labels = clustering.fit_predict(distances)
            num_clusters = len(set(test_labels)) - (1 if -1 in test_labels else 0)
            print(f"阈值 {test_threshold:.2f} -> 分组数 {num_clusters}")
            
            # 选择最接近目标分组数的阈值
            if abs(num_clusters - target_clusters) < abs(best_num_clusters - target_clusters):
                best_threshold = test_threshold
                best_num_clusters = num_clusters
        
        print(f"\n选择最佳阈值: {best_threshold:.2f}")
        
        # 使用最佳阈值进行最终聚类
        clustering = DBSCAN(
            eps=best_threshold,
            min_samples=3,
            metric='precomputed'
        )
        labels = clustering.fit_predict(distances)
        
        # 统计聚类结果
        unique_labels = set(labels)
        noise_count = list(labels).count(-1)
        print(f"聚类完成: 找到 {len(unique_labels) - (1 if -1 in unique_labels else 0)} 个分组")
        print(f"未分组的人脸: {noise_count} 个")
        
        groups = {}
        # 计算每个分组的平均相似度和人脸数量
        for label, image_id, quality in zip(labels, self.image_ids, self.quality_scores):
            if label == -1:  # 未分组的人脸
                continue
            if label not in groups:
                # 初始化分组信息
                groups[label] = {
                    'image_ids': [],
                    'quality_scores': [],
                    'similarity_scores': [],
                    'face_count': 0
                }
            groups[label]['image_ids'].append(image_id)
            groups[label]['quality_scores'].append(quality)
            groups[label]['face_count'] += 1
            
            # 计算该人脸与分组内其他人脸的平均相似度
            group_indices = [i for i, l in enumerate(labels) if l == label]
            if len(group_indices) > 1:
                group_similarities = similarities[group_indices]
                avg_similarity = np.mean(group_similarities)
                groups[label]['similarity_scores'].append(avg_similarity)
        
        # 转换为API需要的格式
        result_groups = []
        for label, group_data in groups.items():
            avg_similarity = np.mean(group_data['similarity_scores']) if group_data['similarity_scores'] else 0.0
            result_groups.append({
                'group_id': str(label),
                'name': f'Group {label}',
                'image_ids': group_data['image_ids'],
                'similarity_score': float(avg_similarity),  # 确保是 float 类型
                'face_count': group_data['face_count']
            })
        
        # 打印每个分组的信息
        print("\n分组详情:")
        for group in result_groups:
            print(f"分组 {group['group_id']}: {group['face_count']} 张图片, "
                  f"相似度: {group['similarity_score']:.2f}")
        
        return result_groups
    
    def save_model(self, path):
        """保存模型到文件"""
        model_data = {
            'face_features': self.face_features,
            'image_ids': self.image_ids,
            'quality_scores': self.quality_scores
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path):
        """从文件加载模型"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        self.face_features = model_data['face_features']
        self.image_ids = model_data['image_ids']
        self.quality_scores = model_data.get('quality_scores', [1.0] * len(self.image_ids)) 