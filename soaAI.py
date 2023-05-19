import folders as folders
import splitfolders
import tensorflow as tf
from tensorflow import keras
import pathlib
from pathlib import Path
import os
import natsort
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from tensorflow.python import keras
from keras.layers import Dense, Flatten, Conv2D
from keras import Model
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras import layers
from keras.layers import preprocessing
from keras.models import Sequential
from keras.optimizers import RMSprop

plus = os.listdir(".\\data+")
plus = natsort.natsorted(plus)

minus = os.listdir(".\\data-")
minus = natsort.natsorted(minus)

pic_box = plt.figure(figsize=(14, 12))
for i, image_name in enumerate(plus[5:10]):
    # 2. считываем текущее изображение
    image = plt.imread(str(Path(".\\data+", image_name)))
    # 3. создаем "подграфик" для вывода текущего изображения в заданной позиции
    ax = pic_box.add_subplot(3, 5, i+1)
    # 4. в качестве названия графика определяем имя фотографии и число каналов
    ax.set_title(str(image_name) + '\n Каналов = ' + str(image.shape[2]))
    # 5. выводим изображение на экран
    plt.imshow(image)
    # 6. отключаем вывод осей графика
    plt.axis('off')

for img in plus:
    im = Image.open(Path(".\\data+", img))
    # Если расширение файла ".png" и формат файла "PNG":
    if img[-3:].lower() == 'png' and im.format == 'PNG':
        # если режим изображения не RGBA (без альфа-канала):
        if im.mode != 'RGBA':
            # конвертируем фото в RGBA и сохраняем в той же директории под тем же именем
            im.convert("RGBA").save(Path(".\\data+", img))
            # при желании, можно вывести имена файлов, которые были переформатированы.
            print(img)

for img in os.listdir(".\\data-"):
    im = Image.open(Path(".\\data-", img))
    # Если расширение файла ".png" и формат файла "PNG":
    if img[-3:].lower() == 'png' and im.format == 'PNG':
        # если режим изображения не RGBA (без альфа-канала):
        if im.mode != 'RGBA':
            # конвертируем фото в RGBA и сохраняем в той же директории под тем же именем
            im.convert("RGBA").save(Path(".\\data-", img))
            # при желании, можно вывести имена файлов, которые были переформатированы.
            print(img)

splitfolders.ratio(".\\data", 'faces_splited', ratio=(0.8, 0.15, 0.05), seed=18, group_prefix=None)

# определим параметры нормализации данных
train = ImageDataGenerator(rescale=1 / 255)
val = ImageDataGenerator(rescale=1 / 255)

# сгенерируем нормализованные данные
train_data = train.flow_from_directory('faces_splited/train', target_size=(299, 299),
                                       class_mode='binary', batch_size=3, shuffle=True)
val_data = val.flow_from_directory('faces_splited/val', target_size=(299, 299),
                                   class_mode='binary', batch_size=3, shuffle=True)

model = Sequential([
    # добавим аугментацию данных
    layers.Conv2D(16, (3, 3), activation='selu', input_shape=(299, 299, 3)),
    layers.MaxPool2D(2, 2),
    layers.Conv2D(32, (3, 3), activation='selu'),
    layers.MaxPool2D(2, 2),
    layers.Dropout(0.05),

    layers.Conv2D(64, (3, 3), activation='selu'),
    layers.MaxPool2D(2, 2),
    layers.Dropout(0.1),
    layers.Conv2D(128, (2, 2), activation='selu'),
    layers.MaxPool2D(2, 2),
    layers.Conv2D(256, (2, 2), activation='selu'),
    layers.MaxPool2D(2, 2),
    layers.Dropout(0.2),
    layers.Flatten(),
    layers.Dense(500, activation='selu'),

    layers.Dense(1, activation='sigmoid')
])

# Файл для сохранения модели с лучшими параметрами
checkpoint_filepath = 'best_model.h5'
# Компиляция модели
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(lr=0.00024),
              # optimizer=tf.keras.optimizers.Adam(learning_rate=0.000244),
              metrics=['binary_accuracy'])

model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    monitor='val_binary_accuracy',
    mode='max',
    save_best_only=True)

# Тренировка модели
history = model.fit(train_data, batch_size=500, verbose=1, epochs=35,
                    validation_data=val_data,
                    callbacks=[model_checkpoint_callback])
