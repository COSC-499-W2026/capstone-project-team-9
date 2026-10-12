# OCR and Scene Check Notes

# OCR

# EasyOCR (pick)

- Installs with pip and has a stable Python API.
- Detects text regions itself, so no separate localization step is needed.
- The `allowlist` parameter (A-Z, 0-9) restricts the character set and cuts down junk reads on short codes.
- Costs: depends on PyTorch, so the install is large. It is slow on CPU, so run it once per image and downscale first.
- Python 3.14 caveat: check that a matching torch wheel exists. If the install fights you, use a 3.12 venv.

# Alternatives and why they're worse

- PaddleOCR: often the most accurate on real photos. PaddlePaddle is a heavy, fussy install, especially on Windows, and the accuracy gain only matters if EasyOCR is still failing after tuning.
- RapidOCR: runs PaddleOCR's models through ONNX Runtime, so you get most of the accuracy without installing PaddlePaddle. First thing to try if EasyOCR can't read the plaques. Downside: smaller community and less documentation.
- docTR: a good free detector plus recognizer. Heavier to set up than EasyOCR with no clear accuracy win for short codes.
- Tesseract: the lightest option, but built for scanned documents, not photos. It needs the plaque to be found and cropped first, which is the hard part, and it handles perspective and glare badly.
- Cloud OCR (Google Vision, Azure): very accurate, but not free past the quota. That breaks the free-tooling requirement and adds a network dependency.


# Scene checker

# OpenCV SIFT + RANSAC (pick)

- Free, needs no model or training data, and the result is explainable: "N inliers after geometric verification."
- Handles scale and rotation changes and moderate viewpoint shift, which fits the "any distance, any angle" requirement.
- SIFT has been in main OpenCV since 4.4 (the patent expired), so contrib is not needed.
- Use Lowe's ratio test (about 0.75) before RANSAC.
- Downscale large images to around 1000px on the long side so runtime stays reasonable.

# Alternatives and why they're wrose

- ORB / AKAZE: faster and lighter, but weaker under scale change, blur, and low light. ORB would likely be flaky on bad-angle photos. AKAZE is a middle ground if SIFT turns out too slow.
- SuperPoint + LightGlue / LoFTR: learned matchers that beat SIFT on wide-baseline pairs. They need PyTorch and weights and are slower on CPU. Only reach for them if SIFT fails on real data.
- CLIP / DINOv2 embeddings (cosine similarity): tolerant of viewpoint changes, but poor at instance-level discrimination, so two similar-looking doors score close. No geometric proof and no explanation of the score. Could work as a cheap prefilter, but not as the verdict.
- Perceptual hash, histogram, SSIM: these break with any change in angle or distance, so they are out given the requirements.
- Fine-tuned Siamese network: only one image per room exists, so there is nothing to train on.
- Cloud vision APIs: not free, add latency, and the results are harder to explain.

# Anti-cheat

- OCR alone is fooled by a handwritten number, so require both checks to pass. They are complementary.
- Camera-only capture blocks gallery uploads.
- A printed photo of the correct door held up to the camera would still pass SIFT. This is probably out of scope for a capstone, but it is worth a sentence in the writeup as a known limitation.