var fileList = new Array();

// when new file is selected, addToFileList will be executed
function addToFileList (obj) {
  if (fileList.length >= 10) {
    alert('You can only upload up to 10 files at a time.');
    return;
  }
  for (var i=0; i < obj.files.length; ++i) {
    var inTheList = false;
    for (var t = 0; t < fileList.length; ++t) {
      if (fileList[t].size == obj.files.item(i).size & fileList[t].name == obj.files.item(i).name){
        inTheList = true;
        alert(obj.files.item(i).name+' is already in the list.');
        break;
      }      
    }
    if (obj.files.item(i).size >= 50*1000*1024){
      alert(obj.files.item(i).name+' is more than the MAX file size limit (50MB).');
    }else{
      // if not in the list yet, add the selected file to the list
      if (!inTheList && fileList.length < 10) { 
        //add isUploaded and errorUpload property
        obj.files.item(i)['isUploaded'] = false;
        obj.files.item(i)['errorUpload'] = false;
        fileList.push(obj.files.item(i)); 
      }
    }    
  }
  if (fileList.length >= 10){
    alert('The maximum number of files to upload at a time is 10.');
  }
  // update the Table
  updateFileTable(fileList);
}

// update fileList Table
function updateFileTable(listFile) {
  var upload_icon = '\
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-cloud-upload" viewBox="0 0 16 16">\
      <path fill-rule="evenodd" d="M4.406 1.342A5.53 5.53 0 0 1 8 0c2.69 0 4.923 2 5.166 4.579C14.758 4.804 16 6.137 16 7.773 16 9.569 14.502 11 12.687 11H10a.5.5 0 0 1 0-1h2.688C13.979 10 15 8.988 15 7.773c0-1.216-1.02-2.228-2.313-2.228h-.5v-.5C12.188 2.825 10.328 1 8 1a4.53 4.53 0 0 0-2.941 1.1c-.757.652-1.153 1.438-1.153 2.055v.448l-.445.049C2.064 4.805 1 5.952 1 7.318 1 8.785 2.23 10 3.781 10H6a.5.5 0 0 1 0 1H3.781C1.708 11 0 9.366 0 7.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383z"/>\
      <path fill-rule="evenodd" d="M7.646 4.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V14.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3z"/>\
    </svg>\
    ';
  var remove_icon = '\
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">\
      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"/>\
      <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"/>\
    </svg>\
  ';
  var progressbar = '\
  <div class="progress" style="width: 100px;">\
    <div id="upload_progress" class="progress-bar progress-bar-striped" role="progressbar" aria-label="File Uploade progressbar" style="width: 0%"></div>\
  </div>\
  ';
  var check_mark = '\
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">\
    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>\
    <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>\
  </svg>\
  ';
  var table = document.getElementsByClassName('file_table');
  var tbody = table[0].getElementsByTagName('tbody');
  var row_td = '';
  for (var i = 0; i < listFile.length; ++i) {
    row_td += '<tr>';
    row_td += '<td class="tbltdEllipsis">' + listFile[i].name + '</td>\n';
    // if file is already uploaded, set width to 100%
    if (listFile[i].isUploaded || listFile[i].errorUpload) {
      progressbar = progressbar.replace('width: 0%', 'width: 100%');
    }
    if (listFile[i].errorUpload) {
      progressbar = progressbar.replace('progress-bar progress-bar-striped', 'progress-bar progress-bar-striped bg-danger');
    }
    // set progressbar id with filename_size
    row_td += '<td>\n' + progressbar.replace("upload_progress", "upload_progress_"+ listFile[i].name +'_'+ listFile[i].size);
    row_td += '</td>\n';
    row_td += '<td> \n';
    row_td += '<button type="button" name="remove_file" onclick="removeFromFileList(this)" ';
    row_td += 'class="btn btn-sm" id="remove_'+ listFile[i].name +'_'+ listFile[i].size;
    row_td += '"> \n';
    row_td += '<i class="bi-trash" style="color: cornflowerblue;"> \n';
    row_td += remove_icon; 
    row_td += '\n</i>\n</button>';
    row_td += '</td>\n'; 
    row_td += '<td> \n';
    if (!listFile[i].isUploaded) {
      row_td += '<button type="button" name="upload_file" onclick="uploadFile(this)" ';
      row_td += 'class="btn btn-sm" id="upload_'+ listFile[i].name +'_'+ listFile[i].size;
      row_td += '"> \n';
      row_td += '<i class="bi-cloud-upload" style="color: cornflowerblue;"> \n';
      row_td += upload_icon; 
      row_td += '\n</i>\n</button>';
    }else{
      row_td += '<i class="bi-check-circle" style="color: green;"> \n';
      row_td += check_mark; 
      row_td += '\n</i>\n';      
    }
    row_td += '</td>\n';
    row_td += '</tr>';
    // set it to width: 0% again for the next file in the table
    progressbar = progressbar.replace('width: 100%', 'width: 0%'); 
    progressbar = progressbar.replace('progress-bar progress-bar-striped bg-danger','progress-bar progress-bar-striped');
  }
  tbody[0].innerHTML = row_td;
}

// when id->remove_file button is clicked, removeFromFileList
function removeFromFileList (obj) {
  var fileobj = obj.id.split('_');
  var lastIdx = fileobj.length - 1;
  var size = fileobj[lastIdx];
  // in cases where filenames has more that 1 '_' in its filename
  var name = '';
  for (var i = 0; i < lastIdx; ++i){
    if (i+1 == lastIdx){
      name+=fileobj[i];
      break;
    }else{name = name + fileobj[i] + '_';}
    // finally, remove the prefix remove_
    name = name.replace('remove_','');
  }
  for (let idx in fileList) {
    if (fileList[idx].name == name && fileList[idx].size == size) {
      // alert('Removing ' + fileList[idx].name + ' - ' + name + '   ' + fileList[idx].size + ' - ' + size);
      fileList.splice(idx, 1); //remove the matched filename
      break;
    }
  }
  // update the Table
  updateFileTable(fileList);
}

// upload individual file
function uploadFile(obj) {
  var fileobj = obj.id.split('_');
  var lastIdx = fileobj.length - 1;
  var size = fileobj[lastIdx];
  // in cases where filenames has more that 1 '_' in its filename
  var name = '';
  for (var i = 0; i < lastIdx; ++i){
    if (i+1 == lastIdx){
      name+=fileobj[i];
      break;
    }else{name = name + fileobj[i] + '_';}
    // finally, remove the prefix upload_
    name = name.replace('upload_','');
  }
  // get file object
  var file = null;
  var fileIdx = null;
  for (let idx in fileList) {
    if (fileList[idx].size == size && fileList[idx].name == name){
      fileList[idx].isUploaded = true;
      file = fileList[idx];
      fileIdx = idx;
      break;
    }
  }
  // disable upload button
  obj.disabled = true;
  // disable remove button
  var remove_button = document.getElementById(obj.id);
  remove_button.disabled = true;
  // get progresbar reference
  var progressbar = document.getElementById('upload_progress_'+name+'_'+size);
  document.cookie = 'filesize='+size;
  var data = new FormData();
  data.append('file', file);
  var request = new XMLHttpRequest();
  request.responseType = 'json';

  // event listener for progress
  request.upload.addEventListener("progress", function(e){
    var loaded = e.loaded;
    var total = e.total;
    var completion = (loaded/total) * 100;
    progressbar.setAttribute('style', 'width: '+ Math.floor(completion) +'%');
  });

  // event listener when completed
  request.addEventListener("load", function(e){
    if (request.status == 200) {
      // alert(name + ' has been uploaded.');
      // when successful, set flags and change upload icon to check mark
      // and activate remove button
      if (fileIdx){
        fileList[fileIdx].isUploaded = true;
        fileList[fileIdx].errorUpload = false;
      }
      updateFileTable(fileList);
      remove_button.disabled = false;
    }else{
      // display error message
      alert(request.status + ' - ' + request.statusText);
      //set file flags for upload and error
      fileList[fileIdx].isUploaded = false;
      fileList[fileIdx].errorUpload = true;
    }
    // set progress bar to red
    progressbar.setAttribute('class', 'progress-bar progress-bar-striped bg-danger');
    remove_button.disabled = false;
    obj.disabled = false;
  });

  request.open('post', '/file/upload');
  // set csrf token
  request.setRequestHeader("x-csrf-token", document.getElementById("csrf_token").value)
  request.send(data);
}

// upload all selected files
function uploadAllFiles(obj) {
  for (let file of fileList){
    // get reference for upload button
    var uploadButton = document.getElementById('upload_'+file.name+'_'+file.size);
    // click the upload button
    if (!file.isUploaded){
      uploadButton.click();
    }
  }
}

// remove already uploaded files from fileList
function removeUploadedFiles(obj){
  var i = fileList.length;
  while(i--){
    if(fileList[i].isUploaded && !fileList[i].errorUpload){
      fileList.splice(i,1);
    } 
  }
  updateFileTable(fileList);
}

