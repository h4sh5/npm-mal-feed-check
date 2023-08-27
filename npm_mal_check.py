#!/usr/bin/env python3

# KEEP THIS AS DEPENDENCY-FREE AS POSSIBLE
import json
import os
import urllib.request
import glob
# KEEP THIS AS DEPENDENCY-FREE AS POSSIBLE

def find_npm_files():
	'''
	find all lockfiles and return a list of paths
	'''
	results = []
	package_lock_json_glob = glob.glob('./**/package-lock.json', recursive=True)
	package_json_glob =  glob.glob('./**/package.json', recursive=True)
	for filepath in package_lock_json_glob:
		results.append(filepath)
	for filepath in package_json_glob:
		results.append(filepath)

	return results

def find_packages_from_package_lock_json(filepath):
	'''
	parse package-lock.json and return a list of tuple of package names and versions
	'''
	names_versions = []
	with open(filepath, 'r') as f:
		try:
			d = json.load(f)
		except Exception as e:
			print(f"ERROR could not json decode {filepath}:", e)
			return []
		for depdendency in d['dependencies']:
			version = d['dependencies'][depdendency]['version']
			names_versions.append((depdendency,version))
	return names_versions

def find_packages_from_package_json(filepath):
	'''
	parse package.json and return a list of tuple of package names and version definitions
	do both dependencies and devDependencies
	'''
	names_versiondefs = []
	with open(filepath, 'r') as f:
		try:
			d = json.load(f)
		except Exception as e:
			print(f"ERROR could not json decode {filepath}:", e)
			return []

		if 'dependencies' in d:
			for depdendency in d['dependencies']:
				version_def = d['dependencies'][depdendency]
				names_versiondefs.append((depdendency,version_def))


		if 'devDependencies' in d:
			for depdendency in d['devDependencies']:
				version_def = d['devDependencies'][depdendency]
				names_versiondefs.append((depdendency,version_def))

	return names_versiondefs



npm_files = find_npm_files()
print('\n'.join(npm_files))

for f in npm_files:
	if f.endswith('package-lock.json'):
		for name, version in find_packages_from_package_lock_json(f):
			print(name, version)
	if f.endswith('package.json'):
		for name, version_def in find_packages_from_package_json(f):
			print(name, version)