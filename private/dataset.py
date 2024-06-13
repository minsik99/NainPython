import tensorflow as tf
import tensorflow_datasets as tfds

# COCO 데이터셋 로드
dataset, info = tfds.load('coco/2017', with_info=True, split='train')

# 데이터셋 전처리 함수
def preprocess(data):
    image = tf.image.resize(data['image'], (256, 256))
    image = tf.cast(image, tf.float32) / 255.0
    keypoints = data['objects']['keypoints']
    return image, keypoints

# 데이터셋 전처리 적용
train_dataset = dataset.map(preprocess).batch(32)

# 모델 정의 (간단한 예시 모델)
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(17 * 3)  # COCO 데이터셋의 키포인트 수
])

# 모델 컴파일
model.compile(optimizer='adam', loss='mse')

# 모델 학습
model.fit(train_dataset, epochs=10)

# 모델 평가 (예시 데이터)
test_dataset = dataset.map(preprocess).batch(32)
loss = model.evaluate(test_dataset)
print(f"Test Loss: {loss}")
