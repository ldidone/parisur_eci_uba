import cv2
import numpy as np
import os
from pdf2image import convert_from_path


class Pdf2Jpg:
    def __init__(self, base_input_path, base_output_path) -> None:
        self.base_input_path = base_input_path
        self.base_output_path = base_output_path
        self.file_paths = self.__get_file_paths()

    def __get_file_paths(self):
        file_paths = os.listdir(self.base_input_path)
        file_paths = [
            f for f in file_paths if os.path.isfile(self.base_input_path + "/" + f)
        ]

    def convert_files(self):
        q_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            file_path_full = f"{base_input_path}/{file_path}"
            print(f"Converting file {file_path_full} | [{i}/{q_files}]")
            images = convert_from_path(file_path_full)
            cv2_images = []
            for image in images:
                img = np.array(image)
                img = img[:, :, ::-1].copy()
                cv2_images.append(img)
            image = cv2.vconcat(cv2_images)
            file_name = file_path.split(".")[0]
            output_path = f"{base_output_path}/{file_name}.jpg"
            cv2.imwrite(output_path, image)
        print("All files were converted successfully!")


if __name__ == "__main__":
    base_input_path = "data/inputs/invoices/pdfs"
    base_output_path = "data/inputs/invoices/jpgs"

    converter = Pdf2Jpg(base_input_path, base_output_path)
    converter.convert_files()
