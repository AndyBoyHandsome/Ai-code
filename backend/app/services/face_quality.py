import cv2
import numpy as np

class FaceQualityAssessor:
    def __init__(self):
        self.min_face_size = 80  # 最小人脸尺寸
        self.blur_threshold = 100  # 模糊度阈值
        self.min_brightness = 40   # 最小亮度
        self.max_brightness = 220  # 最大亮度
        
    def assess_quality(self, image, face):
        """评估人脸质量"""
        score = 1.0
        reasons = []
        
        # 1. 检查人脸大小
        bbox = face.bbox.astype(int)
        face_width = bbox[2] - bbox[0]
        face_height = bbox[3] - bbox[1]
        
        if face_width < self.min_face_size or face_height < self.min_face_size:
            score *= 0.5
            reasons.append("face_too_small")
            
        # 2. 检查模糊度
        face_img = image[bbox[1]:bbox[3], bbox[0]:bbox[2]]
        if face_img.size > 0:
            blur_score = cv2.Laplacian(cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            if blur_score < self.blur_threshold:
                score *= 0.7
                reasons.append("face_blurry")
        
        # 3. 检查亮度
        if face_img.size > 0:
            gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray_face)
            if brightness < self.min_brightness or brightness > self.max_brightness:
                score *= 0.8
                reasons.append("poor_lighting")
        
        # 4. 检查人脸姿态
        landmarks = face.kps
        if landmarks is not None:
            # 计算眼睛和嘴巴的水平对称性
            left_eye = landmarks[0]
            right_eye = landmarks[1]
            
            eye_angle = np.abs(np.arctan2(right_eye[1] - left_eye[1], 
                                         right_eye[0] - left_eye[0]) * 180 / np.pi)
            if eye_angle > 20:  # 如果倾斜角度大于20度
                score *= 0.9
                reasons.append("face_tilted")
        
        return score, reasons

    def is_good_quality(self, image, face, threshold=0.6):
        """判断人脸质量是否合格"""
        score, reasons = self.assess_quality(image, face)
        return score >= threshold, score, reasons 