#!/usr/bin/env python3

# KEEP THIS AS DEPENDENCY-FREE AS POSSIBLE
import json
import os
from urllib.request import Request, urlopen
import glob
import time
import datetime
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

def pull_github_npm_mal_pkgs(past_days=90):
	'''
	get malicious npm packages from the last <past_days> using the github api
	return dict of name and version ranges
	'''

	GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
	headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
	if GITHUB_TOKEN:
		print("using GITHUB_TOKEN to authenticate to API")
		headers["Authorization"] = "Bearer " + GITHUB_TOKEN 
	from_date = datetime.date.today() - datetime.timedelta(days=past_days)
	date_range_str = ">"+from_date.isoformat()
	per_page = 100
	page = 0
	
	# dict of name and a list of version definitions (dictionary is good for faster lookup)
	results = {}
	mal_advisories_url = f"https://api.github.com/advisories?type=malware&updated={date_range_str}&per_page={per_page}&page={page}"

	while True:
		
		print(mal_advisories_url)
		req = Request(mal_advisories_url, None, headers)
		r = urlopen(req)
		if r.status == 200:
			d = json.loads(r.read().decode())
			for item in d:
				for v in item['vulnerabilities']:
					name = v['package']['name']
					version_def = v['vulnerable_version_range']
					if name not in results:
						results[name] = []
					results[name].append(version_def)
			if "Link" in r.headers:
				if 'rel="next"' in r.headers['Link']:
					mal_advisories_url = r.headers['Link'].split('rel="next"')[0].split("<")[1].split('>;')[0]
				else:
					print("done")
					break
			print(len(results),'packages so far')
			# if len(d) < per_page:
			# 	print("done")
			# 	break # done polling
			# page += 1 
			
		else:
			print('ERROR pulling github url:', r.status, r.read().decode())

	return results




all_package_version_defs = {} 


npm_files = find_npm_files()
print('\n'.join(npm_files))

for f in npm_files:
	if f.endswith('package-lock.json'):
		for name, version in find_packages_from_package_lock_json(f):
			if name not in all_package_version_defs:
				all_package_version_defs[name] = []
			all_package_version_defs[name].append(version)

	if f.endswith('package.json'):
		for name, version_def in find_packages_from_package_json(f):
			if name not in all_package_version_defs:
				all_package_version_defs[name] = []
			all_package_version_defs[name].append(version_def)


mal_package_version_defs = pull_github_npm_mal_pkgs()

mal_pkg_count = 0

for name in mal_package_version_defs:
	if name in all_package_version_defs:
		print("MALICIOUS PACKAGE DETECTED:", name, all_package_version_defs[name])
		mal_pkg_count += 1

if mal_pkg_count > 0:
	print(mal_pkg_count, "potentially malicious packages detected")
	exit(2)

print("Nothing bad found.")
