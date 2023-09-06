
function getFileServiceByHash(serviceName, hash){
  // get reference for file_service_info
  var serviceInfo = document.getElementById('file_service_info');
  var messageInfo = '\
  <button class="btn btn-outline-info disabled" type="button">\
    If this file has existing %service_name% info, it will show on the right side panel.\
  </button>\
  '.replace('%service_name%', serviceName);
  serviceInfo.innerHTML = messageInfo;

  // fetch service information of the file
  var request = new XMLHttpRequest();
  request.responseType = 'json';
  request.addEventListener("load", function(e){
    if (request.status == 200) {
      var alertMessage = '\
      <div class="alert {{type}} alert-dismissible fade show" role="alert">  \
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\
        {{message_here}}\
      </div>\
      ';
      var viewSideAlertPanel = document.getElementById('view_side_alert_panel')
      var response = request.response;
      if (response.report.hasOwnProperty('content')){
        // display content here
        if (serviceName == 'Report'){
          alertMessage = alertMessage.replace('{{type}}', 'alert-success')
          viewSideAlertPanel.innerHTML = alertMessage.replace('{{message_here}}', response.message)
          var CKContentButtons = '\
          <ul>\
            <a href="{{edit_link_here}}" class="btn btn-sm btn-outline-warning mt-3" role="button">Edit Report</a>\
            <a href="{{save_pdf_link_here}}" class="btn btn-sm btn-outline-success mt-3" role="button">Save as PDF</a>\
          </ul>';
          // get reference for ck-edit-content for the the Edit Report button
          var getCKEditorView = document.getElementById('ck-content-buttons'); 
          if (response.read_only == 0){
            CKContentButtons = CKContentButtons.replace('{{edit_link_here}}', '/report/edit/'+response.report.id); 
          }else{
            CKContentButtons = CKContentButtons.replace(
              '<a href="{{edit_link_here}}" class="btn btn-sm btn-outline-warning mt-3" role="button">Edit Report</a>',
              '<a href="/report/view/'+response.report.id+'" class="btn btn-sm btn-outline-warning mt-3" role="button">View Report</a>'
            );
          }
          CKContentButtons = CKContentButtons.replace('{{save_pdf_link_here}}', '/report/download/'+response.report.id); 
          getCKEditorView.innerHTML = CKContentButtons;
          // get reference for ck-content
          var ckEditorContent = document.getElementById('ck-content'); 
          ckEditorContent.innerHTML = response.report.content;
          
        }
      }else{
        alertMessage = alertMessage.replace('{{type}}', 'alert-danger');
        viewSideAlertPanel.innerHTML = alertMessage.replace('{{message_here}}', response.error);        
      }
    }else{
      var alertMessage = '\
      <div class="alert alert-danger alert-dismissible fade show" role="alert">  \
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\
        {{message_here}}\
      </div>\
      ';
      // get reference for alert panel
      var viewSideAlertPanel = document.getElementById('view_side_alert_panel');
      if (response){
        viewSideAlertPanel.innerHTML = alertMessage.replace('{{message_here}}', response.error);
      }else{
        viewSideAlertPanel.innerHTML = alertMessage.replace('{{message_here}}', 'You do not have permission to view the report.');
      }
    }
  })
  // alert('/service/'+serviceName.toLowerCase()+'/'+hash);
  var url = '/service/'+ serviceName.toLowerCase() + '/' + hash;
  request.open('get', url);
  // set csrf token
  request.setRequestHeader("x-csrf-token", document.getElementById("csrf_token").value);
  request.send();
}