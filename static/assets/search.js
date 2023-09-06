

function search_myreports() {
    var search = document.getElementById('search');
    if (search.value.length >= 1){
        document.forms['search'].submit();
    }else if(search.value.length == 0) {
        // this is to list back all reports
        search.value = 'all';
        document.forms['search'].submit();
    }
    return true;
}

var search = document.getElementById('search');
if (search) {
    search.focus();
    var val = search.value;
    if (val.toUpperCase() == 'ALL') {
        val = '';
    }
    // this is to put the cursor to end of string
    search.value = '';
    search.value = val;
}
