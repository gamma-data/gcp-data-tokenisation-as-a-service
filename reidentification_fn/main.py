from google.cloud import firestore
from flask import abort

project_id = "data-treatment-as-a-service"

def reidentify(token):
	try:
		db = firestore.Client(project=project_id)
		reid_doc_ref = db.collection(u'reid-store').document(str(token))
		if reid_doc_ref.get().exists:
			return reid_doc_ref.get().get("natural_key")
		else:
			abort(404)
	except Exception as e:
		print(str(e))

def main(request):
	try:
		content_type = request.headers['content-type']
		if content_type == 'application/json':
			request_json = request.get_json(silent=True)
			if request_json and 'token' in request_json:
				name = request_json['token']
			else:
				raise ValueError("JSON is invalid, or missing a 'token' property")
		elif content_type == 'application/octet-stream':
			token = request.data
		elif content_type == 'text/plain':
			token = request.data
		elif content_type == 'application/x-www-form-urlencoded':
			token = request.form.get('token')
		else:
			raise ValueError("Unknown content type: {}".format(content_type))
		return reidentify(token)
	except Exception as e:
		print(str(e))