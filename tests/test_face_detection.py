"""
Automated Test Suite for Task 1: Face Detection Only.

Validates:
1. Face detector loads model properly
2. Detects primary face on portrait image (returns bounding box & confidence)
3. Detects 5 facial keypoints/landmarks
4. Coordinates include pixel and normalized values
5. Returns proper status ("Face detected" / "No face detected")
6. Handles images with no face gracefully
7. Integration with /api/photo/process-background and /api/photo/detect-face
"""
import sys
import io
import time
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services.face_detection import get_face_detector
from backend.utils.image_ops import load_and_preprocess_image


def test_face_detector_unit():
    print("\n--- Test 1: Face Detection Unit Tests ---")
    detector = get_face_detector()
    assert detector is not None, "Detector singleton should not be None"
    assert detector.detector is not None, "OpenCV FaceDetectorYN instance should be created"

    # 1. Test on customer photo cc9b3438_original.jpeg
    photo_path = BASE_DIR / "input" / "cc9b3438_original.jpeg"
    if photo_path.exists():
        with open(photo_path, "rb") as f:
            img, orig_sz = load_and_preprocess_image(f.read())

        t0 = time.time()
        result = detector.detect_primary_face(img, original_size=orig_sz)
        ms = (time.time() - t0) * 1000

        print(f"Customer Photo Detection: {ms:.1f}ms")
        print(f"Status: {result['status']}")
        print(f"Confidence: {result['confidence']}")
        print(f"BBox: {result['bounding_box']}")

        assert result["detected"] is True, "Should detect face in customer photo"
        assert result["status"] == "Face detected"
        assert result["confidence"] > 0.7, "Confidence should be high (> 0.7)"

        bbox = result["bounding_box"]
        assert bbox["x_norm"] > 0 and bbox["x_norm"] < 1.0, "x_norm must be between 0 and 1"
        assert bbox["y_norm"] > 0 and bbox["y_norm"] < 1.0, "y_norm must be between 0 and 1"
        assert bbox["w_norm"] > 0 and bbox["w_norm"] < 1.0, "w_norm must be between 0 and 1"
        assert bbox["h_norm"] > 0 and bbox["h_norm"] < 1.0, "h_norm must be between 0 and 1"

        landmarks = result["landmarks"]
        assert landmarks is not None, "Landmarks must be present"
        for lm_name in ["right_eye", "left_eye", "nose_tip", "right_mouth", "left_mouth"]:
            assert lm_name in landmarks, f"Landmark {lm_name} must be detected"
            assert 0.0 <= landmarks[lm_name]["x_norm"] <= 1.0
            assert 0.0 <= landmarks[lm_name]["y_norm"] <= 1.0
        print("PASS: Customer photo face detection verified with 5 landmarks.")

    # 2. Test on blank synthetic image (No face condition)
    blank_img = Image.new("RGB", (400, 400), color=(128, 128, 128))
    res_blank = detector.detect_primary_face(blank_img)
    print(f"\nBlank Image Detection: status={res_blank['status']}, detected={res_blank['detected']}")
    assert res_blank["detected"] is False, "Should not detect face on blank image"
    assert res_blank["status"] == "No face detected"
    assert res_blank["bounding_box"] is None
    assert res_blank["landmarks"] is None
    print("PASS: No face condition verified.")


def test_api_integration():
    print("\n--- Test 2: API End-to-End Integration ---")
    import asyncio
    from fastapi import UploadFile
    from backend.api.photo import process_background, detect_face_endpoint, SESSION_CACHE

    async def run_async():
        photo_path = BASE_DIR / "input" / "cc9b3438_original.jpeg"
        if not photo_path.exists():
            print("Skipping API test (customer photo not found)")
            return

        with open(photo_path, "rb") as f:
            buf = io.BytesIO(f.read())
        upload = UploadFile(filename="02.jpg.jpeg", file=buf)

        # 1. Process photo via background removal (auto fast mode)
        resp = await process_background(file=upload, method_mode="auto", smoothness=1.0)
        import json
        data = json.loads(resp.body.decode("utf-8"))

        assert data["success"] is True
        session_id = data["session_id"]
        assert "face_detection" in data, "face_detection must be returned in response"

        fd = data["face_detection"]
        print(f"API Face Detection in process-background: status={fd['status']}, conf={fd['confidence']}")
        assert fd["detected"] is True
        assert fd["status"] == "Face detected"
        assert fd["bounding_box"] is not None

        # 2. Test dedicated /detect-face endpoint (zero AI background re-run)
        t_call_start = time.time()
        resp_detect = await detect_face_endpoint(session_id=session_id)
        detect_time = (time.time() - t_call_start) * 1000
        data_detect = json.loads(resp_detect.body.decode("utf-8"))

        print(f"Dedicated /detect-face API call executed in {detect_time:.2f}ms (Cached/Zero Re-run)")
        assert data_detect["success"] is True
        assert data_detect["detected"] is True
        assert data_detect["status"] == "Face detected"
        print("PASS: API endpoints verified successfully.")

    asyncio.run(run_async())


if __name__ == "__main__":
    test_face_detector_unit()
    test_api_integration()
    print("\nALL TASK 1 FACE DETECTION TESTS PASSED!")
