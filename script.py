import cv2
import easyocr
import pandas as pd
import numpy as np
from pdf2jpg import Pdf2Jpg
import time


class OCRInputer:
    def __init__(self, input_path, output_path, csv_path, use_gpu=False) -> None:
        converter = Pdf2Jpg()
        self.base_input_path = input_path
        self.base_output_path = output_path
        self.file_paths = converter.get_file_paths(self.base_input_path)
        self.reader = easyocr.Reader(["es", "en"], gpu=use_gpu)
        self.df = self.__read_csv_data(csv_path)
        self.invoice_numbers = list(self.df.invoice_number)
        self.total_strings = ["Total:"]
        self.error_totals = []
        self.q_recovered_by_name = 0

    def __read_csv_data(self, csv_path):
        df = pd.read_csv(csv_path)
        df.rename(
            columns={
                "Invoice Number": "invoice_number",
                "Total Charged": "total_charged",
            },
            inplace=True,
        )
        return df

    def __export_results(self):
        print("Saving results...")
        self.df.rename(
            columns={
                "invoice_number": "Invoice Number",
                "total_charged": "Total Charged",
            },
            inplace=True,
        )
        full_output_path = (
            f"{self.base_output_path}invoice_numbers_{round(time.time())}.csv"
        )
        self.df.to_csv(full_output_path, index=False)

    def extract_info(self, input_path):
        image = cv2.imread(input_path)
        result = self.reader.readtext(image, paragraph=False)

        invoice_number = None
        total_charged = None
        for res in result:
            if invoice_number and total_charged:
                break
            if not invoice_number:
                for invoice in self.invoice_numbers:
                    if invoice.upper() in res[1].upper():
                        invoice_number = invoice
                        print(f"Invoice number found: {invoice_number}")
            if not total_charged:
                for total in self.total_strings:
                    if total.upper() in res[1].upper():
                        try:
                            total_charged = res[1].split(": ")[1].replace("$", "")
                            total_charged = float(total_charged.replace(",", ""))
                            print(f"Total charged found: {total_charged}")
                        except:
                            print(
                                f"Error ocurred with the total of invoice_number: {invoice_number}"
                            )
                            self.error_totals.append(
                                (input_path, invoice_number, res[1])
                            )
                            continue
        if invoice_number and total_charged:
            self.df.loc[
                self.df.invoice_number == invoice_number, "total_charged"
            ] = total_charged
        elif total_charged:
            file_name = input_path.replace(f"{self.base_input_path}/", "").split(".")[0]
            for invoice in self.invoice_numbers:
                if invoice.upper() in file_name.upper():
                    invoice_number = invoice
                    print(f"Invoice number found: {invoice_number}")
                    break
            if invoice_number:
                self.q_recovered_by_name += 1
                self.df.loc[
                    self.df.invoice_number == invoice_number, "total_charged"
                ] = total_charged

    def exctract_all_inputs(self, n=None):
        q_files = len(self.file_paths[:n]) if n else len(self.file_paths)
        for i, file_path in enumerate(self.file_paths[:q_files]):
            input_path = f"{self.base_input_path}/{file_path}"
            print(f"Exctracting info from file {file_path} | [{i+1}/{q_files}]")
            self.extract_info(input_path)

        q_found = self.df[~self.df["total_charged"].isna()].shape[0]

        print("*" * 50)
        print(f"Found {q_found}/{q_files}")
        print("*" * 50)

        self.__export_results()

        if len(self.error_totals) > 0:
            print("************* Errors *************")
            print(self.error_totals)
        print(f"Recovered by name {self.q_recovered_by_name}")


if __name__ == "__main__":
    base_input_path = "D:/paraisur_eci_uba/data/inputs/invoices/jpgs"
    base_output_path = "data/outputs/"
    csv_path = "data/inputs/2023-06-26-invoice_numbers-final.csv"

    inputer = OCRInputer(base_input_path, base_output_path, csv_path, use_gpu=True)
    inputer.exctract_all_inputs()
