ClassicEditor
  .create( document.querySelector( '#editor' ), {
    // Editor configuration.
    toolbar: {
      items: ['heading','fontBackgroundColor', 'fontColor', 'fontFamily', 'fontSize',
              'highlight', '|', 'blockQuote', 'bold', 'underline', 'strikethrough', 'italic', 'link',
              '|', 'uploadImage', 'mediaEmbed', 'imageTextAlternative', 'toggleImageCaption', 
              '|', 'outdent', 'indent', //'alignment',
              'alignment:left', 'alignment:right', 'alignment:center', 'alignment:justify',
              '|', 'code', 'codeBlock', 'sourceEditing', 'htmlEmbed', '|', 'undo', 'redo', '|',
              'todoList', 'numberedList', 'bulletedList', '|', 'insertTable', 
              'tableColumn', 'tableRow', 'mergeTableCells', 'tableCellProperties', 
              'tableProperties', '|', 'removeFormat', 'selectAll', 'findAndReplace', 'pageBreak', 
              'showBlocks', '|', 'specialCharacters', 'subscript', 'superscript' 
            ],
      // items: ['alignment:left', 'alignment:right', 'alignment:center', 'alignment:justify', 'alignment', 'undo', 'redo', 'blockQuote', 'bold', 'code', 'codeBlock', 'selectAll', 'findAndReplace', 'fontBackgroundColor', 'fontColor', 'fontFamily', 'fontSize', 'heading', 'highlight:yellowMarker', 'highlight:greenMarker', 'highlight:pinkMarker', 'highlight:blueMarker', 'highlight:redPen', 'highlight:greenPen', 'removeHighlight', 'highlight', 'horizontalLine', 'htmlEmbed', 'imageTextAlternative', 'toggleImageCaption', 'uploadImage', 'imageUpload', 'insertImage', 'imageInsert', 'resizeImage:original', 'resizeImage:25', 'resizeImage:50', 'resizeImage:75', 'resizeImage', 'imageResize', 'imageStyle:inline', 'imageStyle:alignLeft', 'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:alignBlockLeft', 'imageStyle:alignBlockRight', 'imageStyle:block', 'imageStyle:side', 'imageStyle:wrapText', 'imageStyle:breakText', 'indent', 'outdent', 'italic', 'link', 'linkImage', 'numberedList', 'bulletedList', 'mediaEmbed', 'pageBreak', 'removeFormat', 'showBlocks', 'sourceEditing', 'specialCharacters', 'restrictedEditingException', 'strikethrough', 'style', 'subscript', 'superscript', 'insertTable', 'tableColumn', 'tableRow', 'mergeTableCells', 'toggleTableCaption', 'tableCellProperties', 'tableProperties', 'todoList', 'underline'],
      shouldNotGroupWhenFull: true,
    },
    // codeBlock: {
    //   languages: [
    //       // Do not render the CSS class for the plain text code blocks.
    //       { language: 'plaintext', label: 'Plain text', class: '' },
    //       // Use the "php-code" class for PHP code blocks.
    //       { language: 'php', label: 'PHP', class: 'php-code' },
    //       // Use the "js" class for JavaScript code blocks.
    //       // Note that only the first ("js") class will determine the language of the block when loading data.
    //       { language: 'javascript', label: 'JavaScript', class: 'js javascript js-code' },
    //       // Python code blocks will have the default "language-python" CSS class.
    //       { language: 'python', label: 'Python' }
    //   ]
    // },
    // style: {
    //   definitions: [
    //         {
    //             name: 'Article category',
    //             element: 'h3',
    //             classes: [ 'category' ]
    //         },
    //         {
    //             name: 'Info box',
    //             element: 'p',
    //             classes: [ 'info-box' ]
    //         },
    //     ]
    // },
    removePlugins: ['MediaEmbedToolbar', 'Markdown']
  } )
  .then( editor => {
    window.editor = editor;
    // Set a custom container for the toolbar.
    // document.querySelector( '.document-editor__toolbar' ).appendChild( editor.ui.view.toolbar.element );
    // document.querySelector( '.ck-toolbar' ).classList.add( 'ck-reset_all' );
    // Display all available toolbar items
    // console.log(Array.from(editor.ui.componentFactory.names()));
  } )
  .catch( handleSampleError );

function handleSampleError( error ) {
  const issueUrl = 'https://github.com/ckeditor/ckeditor5/issues';

  const message = [
    'Oops, something went wrong!',
    `Please, report the following error on ${ issueUrl } with the build id "q0f3dforbh3s-u9490jx48w7r" and the error stack trace:`
  ].join( '\n' );

  if (!error){
    console.error( message );
    console.error( error );
  }
}
