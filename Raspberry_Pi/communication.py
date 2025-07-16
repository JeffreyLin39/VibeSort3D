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
    try:
        response = stub.UploadImage(request)
        if not response or not response.result:
            print(f"Empty or invalid response for image_id {image_id}")
            return (image_id, "error")
        image_id = response.image_id  
        raw_result = response.result  

        color = raw_result.strip("{}").split(":")[-1].strip()

        result_tuple = (image_id,color)
        return result_tuple
    except grpc.RpcError as e:
        return (image_id, "error")

