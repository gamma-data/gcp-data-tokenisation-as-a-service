from google.cloud import firestore
import hashlib, uuid

project_id = "data-treatment-as-a-service"

def deidentify(natural_key):
	# get hash of natural_key
	nk_hash = hashlib.sha256(str(natural_key).encode('UTF-8')).hexdigest()

	# check deid store
	db = firestore.Client(project=project_id)
	deid_doc_ref = db.collection(u'deid-store').document(nk_hash)
	if not deid_doc_ref.get().exists:
		# [store miss] generate token for input data type
		guid = uuid.uuid4()
		if type(natural_key) is str:
			token = str(guid) 
		elif type(natural_key) is int:
			token = guid.int & (1<<63)-1
		elif type(natural_key) is float:
			token = float(guid.int & (1<<63)-1)
		else:
			token = str(guid)
		# insert into deid store
		deid_doc_ref.set({u'token': token})
		# insert into reid store
		reid_doc_ref = db.collection(u'reid-store').document(str(token))
		reid_doc_ref.set({u'natural_key': natural_key})
		return token
	else:
		# [store hit] return token
		return deid_doc_ref.get().get("token")

def main(request):
	content_type = request.headers['content-type']
	if content_type == 'application/json':
		request_json = request.get_json(silent=True)
		if request_json and 'natural_key' in request_json:
			name = request_json['natural_key']
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
	return deidentify(natural_key)