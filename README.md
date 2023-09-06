
# Skittish - Report Repository

Is a Python Flask application for report creation and storage using the CKEditor Rich Text Editor. This application is for people in cybersecurity who writes their file analysis and export them to PDF. It also uses wkhtmltopdf application that export the created report to PDF.

![Sample Preview](https://github.com/gegcars/skittish/blob/main/report_preview.png?raw=true)

# WorkFlow
Upload a File to Analyze --> Skittish will create a report template --> Own and start editing the report

# How-To
Install the app<br>
`pip install -r requirements.txt`

Run the app as a desktop application:
`$ export FLASK_APP=skittish FLASK_DEBUG=1`

Creating your custom CKEditor:<br>
https://ckeditor.com/ckeditor-5/online-builder/

Install wkhtmltopdf:
https://github.com/wkhtmltopdf/wkhtmltopdf
`sudo apt install wkhtmltopdf`
`pip install pdfkit`

Admin account can be found in `__init__.py`

Please note that this has only been tested on WSL2 setup. If you test it on Windows, please let me know how it goes. =)

This application is ready to be expanded to other Service such as:
1. Scanning the files using Yara rules or other custom file parser that you have.
2. Querying the file's hash in VirusTotal for more information that will help the analysis faster.
3. Sending files to Sandboxes and parse the Sandbox report.
4. And so on...

You can also checkout the sample PDF file that can be found in `download` folder.

To write your own service, just go to the `services` folder.


**Note**:<br>
*This is my attempt on learning MORE about Flask and creating RESTful web service API.*

<br><br>
References:<br>
https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
https://getbootstrap.com/docs/5.3/examples/
https://mdbootstrap.com/docs/standard/extended/dropdown-multilevel/
https://ckeditor.com/ckeditor-5/online-builder/
https://gist.github.com/Julian-Nash/e94e181621e41f002c5848e2787c3a36
https://stackoverflow.com/questions/3031219/recursively-access-dict-via-attributes-as-well-as-index-access
