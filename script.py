import cv2
import easyocr
import pandas as pd
import numpy as np
from pdf2jpg import Pdf2Jpg


class InvoiceData:
     def __init__(self, invoice_number, total_charged) -> None:
          self.invoice_number=invoice_number
          self.total_charged=total_charged

class OCRInputer:
     def __init__(self, input_path, output_path, csv_path, use_gpu=False) -> None:
          converter = Pdf2Jpg()
          self.base_input_path = input_path
          self.base_output_path = output_path
          self.file_paths = converter.get_file_paths(self.base_input_path)
          self.reader = easyocr.Reader(["es", "en"], gpu=use_gpu)
          self.df = self.__read_csv_data(csv_path)
          self.invoice_numbers = list(self.df.invoice_number)

     def extract_info(self, input_path, output_path, verbose=False):
          image = cv2.imread(input_path)
          result = self.reader.readtext(image, paragraph=False)

          invoice_number = None
          total_charged = np.NaN
          for res in result:
               if verbose:
                    print("res:", res)

               pt0 = res[0][0]
               pt1 = res[0][1]
               pt2 = res[0][2]
               pt3 = res[0][3]
               pt0 = [round(pto) for pto in pt0]
               pt1 = [round(pto) for pto in pt1]
               pt2 = [round(pto) for pto in pt2]
               pt3 = [round(pto) for pto in pt3]
               cv2.rectangle(image, pt0, (pt1[0], pt1[1] - 23), (166, 56, 242), -1)
               cv2.putText(image, res[1], (pt0[0], pt0[1] - 3), 2, 0.8, (255, 255, 255), 1)
               cv2.rectangle(image, pt0, pt2, (166, 56, 242), 2)

               """if res[1] in self.invoice_numbers:
                    invoice_number = res[1]
               elif res[1].split(':')[1].replace(' ', '') in self.invoice_numbers:
                    invoice_number = res[1].split(':')[1].replace(' ', '')"""
                
          cv2.imwrite(output_path, image)
          if invoice_number is not None:
               print(f'INVOICE NUMBER: {invoice_number}')

     def exctract_all_inputs(self, n):
          q_files = len(self.file_paths[:n])
          for i, file_path in enumerate(self.file_paths[:n]):
               input_path = f"{self.base_input_path}/{file_path}"
               output_path = f"{self.base_output_path}/{file_path}"
               print(f"Exctracting info from file {file_path} | [{i+1}/{q_files}]")
               self.extract_info(input_path, output_path, verbose=False)
     
     def __read_csv_data(self, csv_path):
          df = pd.read_csv(csv_path)
          df.rename(columns={'Invoice Number': 'invoice_number',
                              'Total Charged': 'total_charged'}, inplace=True)
          return df


if __name__ == "__main__":
    base_input_path = "data/inputs/invoices/jpgs"
    base_output_path = "data/outputs/jpgs"
    csv_path = "data/inputs/2023-06-26-invoice_numbers-final.csv"

    inputer = OCRInputer(base_input_path, base_output_path, csv_path)
    inputer.exctract_all_inputs(n=5)