from plate_recognition_core.Reader import Reader
from plate_recognition_core.LicensePlateValidator import LicensePlateValidator 
from plate_recognition_core.CanonicalCorrelationAnalyzer import CanonicalCorrelationAnalyzer
from plate_recognition_core.ImageDisplay import ImageDisplay
from plate_recognition_core.ImageSaver import ImageSaver
from plate_recognition_core.ResizedToOriginalMapper import ResizedToOriginalMapper
from plate_recognition_core.CharactersSegmentator import CharactersSegmentator
from plate_recognition_core.CharactersModel import CharactersModel
from plate_recognition_core.ModelMapper import ModelMapper
from plate_recognition_core.Predictor import Predictor 

import os
import matplotlib.pyplot as plt
from skimage.morphology import opening, square, closing

class ImageAnalyzer():
    def __init__(self, character_recognition_model_path, allowed_mistake_on_license_plate_ratio, reset_between_predictions):
        self.__character_recognition_model_path = character_recognition_model_path
        self.__allowed_mistake_on_license_plate_ratio = allowed_mistake_on_license_plate_ratio
        self.__reset_between_predictions = reset_between_predictions
        self.__detected_license_plates = []

    def analyze_uploaded_image(self, image_path):

        if self.__reset_between_predictions == True:
            self.__detected_license_plates = []
            
        reader = Reader(image_path)
        binary_image = reader.get_binary()
        # ImageDisplay.show_image(binary_image)
        binary_image_resized = reader.get_binary_resized(1)

        license_plate_validator = LicensePlateValidator(
            allowed_mistake_on_ratio = self.__allowed_mistake_on_license_plate_ratio, 
            white_to_black_results_path = './data_utils/results.json'
        )
        cca = CanonicalCorrelationAnalyzer(binary_image_resized, license_plate_validator)

        plate_like_objects_coordinates = cca.find_plate_like_objects_coordinates()
        plate_like_object_images = ResizedToOriginalMapper(binary_image).get_plate_like_objects_by_coordinates(plate_like_objects_coordinates)

        valid_plate_like_object_images = list(filter(license_plate_validator.validate_plate_like_objects, plate_like_object_images))

        segmentator = CharactersSegmentator(CharactersModel())
        predictor = Predictor(ModelMapper(), model_path = self.__character_recognition_model_path)

        for each_plate_like_object_image in valid_plate_like_object_images:
            ImageDisplay.show_image(each_plate_like_object_image)
            
            characters_matrix = segmentator.get_characters_from_license_plate(each_plate_like_object_image)
            predictor.clasify_characters(characters_matrix)
            self.__detected_license_plates.append(predictor.get_classified_characters())

        temp = self.__detected_license_plates
        self.__detected_license_plates = list(filter(lambda x: len(x) < 9, temp))

        return self.__detected_license_plates
