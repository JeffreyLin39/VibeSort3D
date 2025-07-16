# comms.py
import grpc
import cv2
import bin_controller_pb2 as pb
import bin_controller_pb2_grpc as pb_grpc

#Hardcoded with Kevin's Laptop IP
SERVER_ADDRESS = "10.31.28.195:50051"

channel = grpc.insecure_channel(SERVER_ADDRESS)
stub = pb_grpc.BinControllerStub(channel)

def classify_crop(image_id, crop):
    _, buf = cv2.imencode(".jpg", crop)
    image_bytes = buf.tobytes()

    request = pb.UploadImageRequest(image_id=image_id, image_data=image_bytes)
    response = stub.UploadImage(request)
    return response.result
