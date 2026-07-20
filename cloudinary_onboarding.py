import cloudinary
import cloudinary.uploader
import cloudinary.api

# 1. Configure Cloudinary inline with collected credentials
cloudinary.config(
    cloud_name="plsnf1ox",
    api_key="453189513951128",
    api_secret="dwyNIuT78NKOaM7mGB5oJWeAF_E",
    secure=True
)

def run_onboarding():
    print("--- 2. Uploading Image ---")
    sample_image_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    
    # Uploading sample image to Cloudinary
    upload_result = cloudinary.uploader.upload(
        sample_image_url,
        folder="afflux_onboarding"
    )
    
    public_id = upload_result.get("public_id")
    secure_url = upload_result.get("secure_url")
    
    print(f"Secure URL: {secure_url}")
    print(f"Public ID: {public_id}\n")

    print("--- 3. Getting Image Details ---")
    # Fetching explicit structural metadata from Cloudinary API
    image_details = cloudinary.api.resource(public_id)
    
    print(f"Width: {image_details.get('width')}px")
    print(f"Height: {image_details.get('height')}px")
    print(f"Format: {image_details.get('format')}")
    print(f"File Size: {image_details.get('bytes')} bytes\n")

    print("--- 4. Transforming the Image ---")
    # f_auto: Automatically delivers the best format based on the browser (WebP, AVIF, etc.)
    # q_auto: Automatically optimizes image quality compression while saving visual integrity
    transformed_url = cloudinary.CloudinaryImage(public_id).build_url(
        fetch_format="auto", 
        quality="auto"
    )
    
    print("Done! Click link below to see optimized version of the image. Check the size and the format.")
    print(f"Transformed URL: {transformed_url}")

if __name__ == "__main__":
    run_onboarding()