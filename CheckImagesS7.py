	#!/usr/bin/env python3

import os
import random
import re
import time
import pickle
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


myfile = "ST2V7_VKGB_SKU_FULL_ENG_20260609_211447_195.xml"
vurl1 = "https://raja.scene7.com/is/image/Raja/"
vurl2 = "http://raja.scene7.com/is/content/Raja/"
execute_cleaning = True # True pour nettoyer le fichier et False pour utiliser le fichier nettoyé
choice = "ImagesWEB" # AC_Information ou ImagesWEB
output_file_path =''
alreadychecked_urls = "alreadychecked_urls.pkl"
set_urls_valides = pickle.load(open(alreadychecked_urls, "rb"))


def read_target_file(directory, filename):
	file_path = os.path.join(directory, filename)

	try:
		with open(file_path, "r", encoding="utf-8") as file_handle:
			content = file_handle.read()
	except FileNotFoundError:
		print(f"Fichier introuvable: {file_path}")
		return None
	except OSError as err:
		print(f"Erreur lors de la lecture du fichier {file_path}: {err}")
		return None

	return content

def extract_imageweb_values(cleaned_file_path):
	try:
		with open(cleaned_file_path, "r", encoding="utf-8") as file_handle:
			soup = BeautifulSoup(file_handle.read(), "xml")
	except OSError as err:
		print(f"Erreur lors de l'ouverture du fichier {cleaned_file_path}: {err}")
		return []

	imageweb_values = []

	for product_node in soup.find_all("product"):
		vsku = product_node.get("sku") if product_node else None
		tag = product_node.find("custom-attribute", {"name": "ImagesWEB"})
		value = tag.text if tag else None

		if value and vsku:
			imageweb_values.append(value + "|" + vsku)

	return imageweb_values


def extract_attachement_values(cleaned_file_path):
	try:
		with open(cleaned_file_path, "r", encoding="utf-8") as file_handle:
			soup = BeautifulSoup(file_handle.read(), "xml")
	except OSError as err:
		print(f"Erreur lors de l'ouverture du fichier {cleaned_file_path}: {err}")
		return []

	attachement_values = []

	for product_node in soup.find_all("product"):
		vsku = product_node.get("sku") if product_node else None
		for attribute_name in ["AC_Information_1_Value", "AC_Information_2_Value"]:
			tag = product_node.find("custom-attribute", {"name": attribute_name})
			value = tag.text if tag else None

			if value and vsku:
				attachement_values.append(value + "|" + vsku)
	return attachement_values


def write_error_log(log_file_path, message):
	with open(log_file_path, "a", encoding="utf-8") as file_handle:
		file_handle.write(message + "\n")


def check_scene7_urls(imageweb_values, log_file_path, set_urls_valides):

	for imageweb_value in tqdm(imageweb_values, desc="Verification S7", unit="url"):
		left_part, vsku = imageweb_value.split("|", 1)
		url = vurl1 + left_part
		if url in set_urls_valides:
			continue
		else:
			try:

				response = requests.get(url, timeout=10)
				if response.status_code != 200:
					write_error_log(log_file_path, f"Sku : {vsku} not found in S7 {imageweb_value}")
				else:
						set_urls_valides.add(url)
			except requests.RequestException:
				write_error_log(log_file_path, f"Sku : {vsku} not found in S7 {imageweb_value}")

			time.sleep(random.uniform(0.1, 0.5))
	pickle.dump(set_urls_valides, open(alreadychecked_urls, 'wb'))


def check_scene7_attachement(attachement_values, log_file_path):
	for attachement_value in tqdm(attachement_values, desc="Verification S7 Attachement", unit="url"):
		left_part, vsku = attachement_value.split("|", 1)
		url = vurl2 + left_part

		try:
			response = requests.get(url, timeout=10)
			if response.status_code != 200:
				write_error_log(log_file_path, f"Sku : {vsku} not found in S7 {attachement_value}")
		except requests.RequestException:
			write_error_log(log_file_path, f"Sku : {vsku} not found in S7 {attachement_value}")

		time.sleep(random.uniform(0.1, 0.5))
	print('stockage liste des urls bonnes')
	pickle.dump(set_urls_valides, open(alreadychecked_urls, 'wb'))


if __name__ == "__main__":
	output_file_path = myfile + '.clean'
	
	if choice == "ImagesWEB" :
		imageweb_values = extract_imageweb_values(output_file_path)
		print(f"Nombre de valeurs ImageWEB trouvees: {len(imageweb_values)}")
		error_log_file = f"{myfile}.errors.log"
		check_scene7_urls(imageweb_values, error_log_file, set_urls_valides)
	if choice == "AC_Information" :
		attachement_values = extract_attachement_values(output_file_path)
		print(f"Nombre de valeurs AC_Information trouvees: {len(attachement_values)}")
		error_log_file =f"{myfile}.errors.log"
		check_scene7_attachement(attachement_values, error_log_file)
	if choice == "Image2" :
		pass


### rajouter une fonction qui stocke les bonnes URLs dans un tableau et le sauvegarde