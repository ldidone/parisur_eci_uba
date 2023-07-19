import cv2
import numpy as np
import os
from pdf2image import convert_from_path


class Pdf2Jpg:
    def __init__(self, base_output_path=None) -> None:
        self.base_output_path = base_output_path

    def get_file_paths(self, input_path):
        file_paths = os.listdir(input_path)
        file_paths = [f for f in file_paths if os.path.isfile(input_path + "/" + f)]
        return file_paths

    def convert_files(self, input_path):
        file_paths = self.get_file_paths(input_path)
        q_files = len(file_paths)
        for i, file_path in enumerate(file_paths):
            file_path_full = f"{input_path}/{file_path}"
            print(f"Converting file {file_path_full} | [{i+1}/{q_files}]")
            images = convert_from_path(file_path_full)
            cv2_images = []
            for image in images:
                img = np.array(image)
                img = img[:, :, ::-1].copy()
                cv2_images.append(img)
            image = cv2.vconcat(cv2_images)
            file_name = file_path.split(".")[0]
            output_path = f"{self.base_output_path}/{file_name}.jpg"
            cv2.imwrite(output_path, image)
        print("All files were converted successfully!")


if __name__ == "__main__":
    base_input_path = "D:/paraisur_eci_uba/data/inputs/invoices/pdfs"
    base_output_path = "D:/paraisur_eci_uba/data/inputs/invoices/jpgs"

    converter = Pdf2Jpg(base_output_path)
    converter.convert_files(base_input_path)
