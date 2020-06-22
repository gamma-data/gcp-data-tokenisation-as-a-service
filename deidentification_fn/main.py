from google.cloud import firestore
import hashlib, uuid, os
from flask import abort

project_id = "data-treatment-as-a-service"

def deidentify(natural_key, debug):
	try:
		# get hash of natural_key
		nk_hash = hashlib.sha256(str(natural_key).encode('UTF-8')).hexdigest()
		if debug: print("nk_hash = %s" % (nk_hash))
		# check deid store
		db = firestore.Client(project=project_id)
		deid_doc_ref = db.collection(u'deid-store').document(nk_hash)
		if not deid_doc_ref.get().exists:
			if debug: print("token not found, generating...")
			# [store miss] generate token for input data type
			guid = uuid.uuid4()
			if debug: print("guid = %s" % (str(guid)))
			if type(natural_key) is str:
				if debug: print("type = string")
				token = str(guid) 
				print("token = %s" % (token))
			elif type(natural_key) is int:
				if debug: print("type = int")
				token = guid.int & (1<<63)-1
				if debug: print("token = %s" % (str(token)))
			elif type(natural_key) is float:
				if debug: print("type = float")
				token = float(guid.int & (1<<63)-1)
				if debug: print("token = %s" % (str(token)))
			else:
				if debug: print("type = unknown")
				token = str(guid)
				print("token = %s" % (token))
			# insert into deid store
			if debug: print("inserting into deid store...")
			deid_doc_ref.set({u'token': token})
			# insert into reid store
			if debug: print("inserting into reid store...")
			reid_doc_ref = db.collection(u'reid-store').document(str(token))
			reid_doc_ref.set({u'natural_key': natural_key})
			return token
		else:
			# [store hit] return token
			if debug: print("token found, returning...")
			if debug: print("token = %s" % (str(deid_doc_ref.get().get("token"))))
			return deid_doc_ref.get().get("token")
	except Exception as e:
		print(str(e))
		abort(500)

def main(request):
	try:
		if os.getenv('DEBUG', default=None) is not None:
			debug = True
		else:
			debug = False
		content_type = request.headers['content-type']
		if debug: print("content_type = %s" % (content_type))
		if content_type == 'application/json':
			request_json = request.get_json(silent=True)
			if debug: print("request_json = %s" % (str(request_json)))
			if request_json and 'natural_key' in request_json:
				natural_key = request_json['natural_key']
			else:
				raise ValueError("JSON is invalid, or missing a 'natural_key' property")
		elif content_type == 'application/octet-stream':
			natural_key = request.data
		elif content_type == 'text/plain':
			natural_key = request.data
		elif content_type == 'application/x-www-form-urlencoded':
			natural_key = request.form.get('natural_key')
		else:
			raise ValueError("Unknown content type: {}".format(content_type))
		if debug: print("natural_key = %s" % (natural_key))
		token = deidentify(natural_key, debug)
		if debug: print("token = %s" % (str(token)))
		return token
	except Exception as e:
		print(str(e))
		abort(500)
