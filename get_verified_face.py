import face_recognition
import numpy
from PIL import Image, ImageDraw
from shapely.geometry import Polygon

pixels_per_mm = 15


def return_verified_face(img: Image):
    """
    Checks received image for faces. If face was found - performs basic face verification and remove photos that
    definitely could not fit as passport photos. Does not verify background color, as this could be easily edited.
    It accepts only photos with one person on it. The idea behind that is that faces of people where more then one
    person is on - with huge probability does not fulfill passport requirements.

    :param img: image to verify
    :return:    cropped and resized image if it could potentially serve as passport photo, None otherwise
    """
    global pixels_per_mm

    img_width = 35 * pixels_per_mm
    img_height = 45 * pixels_per_mm
    head_ratio = 0.44
    top_ratio = (1 - head_ratio) / 2 * 1.2
    bottom_ratio = (1 - head_ratio) / 2 * 0.8

    face_locations = face_recognition.face_locations(numpy.array(img))

    if not len(face_locations) == 1:
        return None

    for top, right, bottom, left in face_locations:
        ratio = img_height * head_ratio / (bottom - top)
        # Use only photos which size have to be increased max. 2 times
        if ratio > 2:
            return None

        scaled_img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.ANTIALIAS)
        y_center_axe = (right - left) * ratio / 2 + left * ratio

        cropped_img = scaled_img.crop((y_center_axe - img_width / 2, top * ratio - img_height * top_ratio,
                                       y_center_axe + img_width / 2, bottom * ratio + img_height * bottom_ratio))

        face_landmarks_list = face_recognition.face_landmarks(numpy.array(cropped_img))

        if not len(face_landmarks_list) == 1:
            return
        face_landmarks = face_landmarks_list[0]

        if not basic_face_verification(face_landmarks):
            return None
        return cropped_img


def basic_face_verification(landmarks: dict):
    """
    Performs very basic face verification. The aim is to get only faces that look straight into the camera and have
    neutral facial expression.

    :param landmarks:   dictionary of face landmarks
    :return:            true if verification was successful - false otherwise
    """
    if not verify_nose_bridge(landmarks['nose_bridge']) or not \
            verify_eyebrows(landmarks['left_eyebrow'], landmarks['right_eyebrow']) or not \
            verify_lips(landmarks['top_lip'], landmarks['bottom_lip']) or not \
            verify_chin(landmarks['chin'], landmarks['left_eye'], landmarks['right_eye']):
        return False
    return True


def verify_eyebrows(left_eyebrow: list, right_eyebrow: list):
    """
    Verifies if head is not rotated to the side by checking if eyebrows have approximately the same length.

    :param left_eyebrow:   list of points describing left eyebrow geometry
    :param right_eyebrow:  list of points describing right eyebrow geometry
    :return:               true if head seems to look straight - false otherwise
    """
    if not (len(left_eyebrow) == 5 and len(right_eyebrow) == 5):
        raise Exception("Unexpected eyebrows description")
    if left_eyebrow[4][0] - left_eyebrow[0][0] - (right_eyebrow[4][0] - right_eyebrow[0][0]) > 2.5 * pixels_per_mm:
        return False
    return True


def verify_lips(top_lip: list, bottom_lip: list):
    """
    Verifies if the mouth is closed.

    :param top_lip:     list of points describing top lip geometry
    :param bottom_lip:  list of points describing bottom lip geometry
    :return:            true if mouth is closed - false otherwise
    """
    if not (len(top_lip) == 12 and len(bottom_lip) == 12):
        raise Exception("Unexpected lips description")
    mouth_opening = top_lip[7:] + bottom_lip[7:]
    if Polygon(mouth_opening).area > pixels_per_mm * 20:
        return False
    return True


def verify_nose_bridge(nose_bridge: list):
    """
    Verifies if the nose is straight: neck is not bent and the head rotated to the side.

    :param nose_bridge: list of points describing nose bridge geometry
    :return:            true if nose is straight - false otherwise
    """
    if not len(nose_bridge) == 4:
        raise Exception("Unexpected nose bridge description")
    if abs(nose_bridge[3][0] - nose_bridge[0][0]) > pixels_per_mm * 0.8:
        return False
    return True


def verify_chin(chin: list, left_eye: list, right_eye: list):
    """
    Verifies if the neck is not bent to the side not to the back / front.

    :param chin:       list of points describing chin geometry
    :param left_eye:   list of points describing left eye's geometry
    :param right_eye:  list of points describing right eye's geometry
    :return:           true if neck is straight - false otherwise
    """
    if not len(chin) == 17:
        raise Exception("Unexpected chin description")
    if not len(left_eye) == 6 and not len(right_eye) == 6:
        raise Exception("Unexpected eyes description")

    if abs(chin[0][1] - chin[16][1]) > pixels_per_mm * 3:
        return False

    eyes_avg_h = abs(left_eye[0][1] - right_eye[3][1]) / 2 + min(left_eye[0][1], right_eye[3][1])
    eyes_avg_w = abs(left_eye[0][0] - right_eye[3][0]) / 2 + min(left_eye[0][0], right_eye[3][0])
    chin_avg_h = abs(chin[0][1] - chin[16][1]) / 2 + min(chin[0][1], chin[16][1])
    chin_avg_w = abs(chin[0][0] - chin[16][0]) / 2 + min(chin[0][0], chin[16][0])

    if abs(eyes_avg_h - chin_avg_h) > pixels_per_mm * 1.5 or abs(eyes_avg_w - chin_avg_w) > pixels_per_mm:
        return False
    return True

