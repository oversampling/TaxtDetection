from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

# Use the model
model.train(data="config.yml", epochs=3)  # train the model
metrics = model.val()  # evaluate model performance on the validation set

path = model.export(format="pt")  # export the model to ONNX format
results = model("./data/test/images/00020.jpg")  # predict on an image
print(results)