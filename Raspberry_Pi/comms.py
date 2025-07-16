import grpc
import bin_controller_pb2 as pb
import bin_controller_pb2_grpc as pb_grpc
import os

def upload_image(image_path, server_address="10.31.28.195:50051"):
    # Read the image file
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Get image ID from the filename (e.g., "lego_42")
    image_id = os.path.splitext(os.path.basename(image_path))[0][5:]

    # Connect to the local gRPC server
    channel = grpc.insecure_channel(server_address)
    stub = pb_grpc.BinControllerStub(channel)

    # Create and send the gRPC request
    request = pb.UploadImageRequest(image_id=image_id, image_data=image_data)
    try:
        response = stub.UploadImage(request)
        print("✅ UploadImage Response:")
        print(response)
        # print("  Status :", response.status)
        # print("  Result :", response.result)
        # print("  ImageId:", response.image_id)
    except grpc.RpcError as e:
        print("❌ gRPC call failed:", e.details())
        print("  Code:", e.code())

# Example usage
if __name__ == "__main__":
    upload_image("lego_4.jpg")
