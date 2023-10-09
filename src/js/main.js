// GLOBALS
var EditButtonOn = false
var AddRowButtonOn = false
var AddFieldButtonOn = false
var SaveTableButtonOn = false
var DeleteAllButtonOn = false
var deleted_id_list = new Array();
var blue = '#008a96'
var orange = '#c77153'
var grey = '#55565a'

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAIN TABLE SORTER FUNCTION + widgit functionality
///////////////////////////////////////////////////////////////////////////////////////////////////////////

//https://mottie.github.io/tablesorter/docs/example-widget-output.html
//https://mottie.github.io/tablesorter/docs/example-parsers-dates.html
//https://mottie.github.io/tablesorter/docs/example-ajax.html
//https://mottie.github.io/tablesorter/docs/example-update-all.html

var editable_focused = function(txt, columnIndex, $element) {
  // $element is the div, not the td
  // to get the td, use $element.closest('td')
  $element.addClass('focused');
};

var editable_blur = function(txt, columnIndex, $element) {
  // $element is the div, not the td
  // to get the td, use $element.closest('td')
  $element.removeClass('focused');
};

var editable_selectAll = function(txt, columnIndex, $element) {
  // note $element is the div inside of the table cell, so use $element.closest('td') to get the cell
  // only select everthing within the element when the content starts with the letter "B"
  return /^b/i.test(txt) && columnIndex === 0;
};

var sort_start_end = function(e) {
  vis = e.type === "sortBegin";
};

var filter_start_end = function(e, filter) {
  if (e.type === 'filterStart') {
    start = e.timeStamp;
    vis = true;
    t = '<li>Filter Started: [' + filter + ']</li>';
  } else if (start) {
    vis = false;
    t = '<li>Filter Ended after ' + ( (e.timeStamp - start)/1000 ).toFixed(2) + ' seconds</li>';
    start = 0;
    console.log(t)
  } else {
    return;
  }
  
  $("#display").append(t).find('li:first').remove();
};

var tog = function(vis) {
    vis = !vis;
    $.tablesorter.isProcessing($("table"), vis);
};

var dataSearch = function() {
    var search = $(this).attr('data-search').split(',');
    $('table').trigger('search', [search]);
    return false;
};

var editCell = function(event, config) {
  var $this = $(this),
    newContent = $this.text(),
    cellIndex = this.cellIndex, // there shouldn't be any colspans in the tbody
    rowIndex = $this.closest('tr').attr('id'); // data-row-index stored in row id

    console.log(newContent);
  // Do whatever you want here to indicate
  // that the content was updated
  $this.addClass( 'editable_updated' ); // green background + white text
  setTimeout(function() {
    $this.removeClass( 'editable_updated' );
  }, 500);
};

function tableSorterInit(table){

  // formats the html table filled with db info t
  // table sorter. https://mottie.github.io/tablesorter/docs/

  var t, start, vis = false;
  table.tablesorter({
    showProcessing: true,
    theme : 'blue',
    // initialize zebra and filter widgets
    widgets: ["zebra", "filter","editable"],
    widgetOptions : {
      filter_reset : '.reset',
      filter_external : '.search',
      filter_defaultFilter: { 1 : '~{query}' },
      // include column filters
      filter_columnFilters: true,
      filter_placeholder: { search : 'Search...' },
//      filter_saveFilters : true, //This is for some reason getting rid of the table
      filter_reset: '.reset' ,
      // include editable functions
      editable_columns : false,//Array.from(Array(10).keys()), //false,
      editable_enterToAccept : true,          // press enter to accept content, or click outside if false
      editable_autoAccept    : false,          // accepts any changes made to the table cell automatically (v2.17.6)
      editable_autoResort    : false,         // auto resort after the content has changed.
      editable_validate      : null,          // return a valid string: function(text, original, columnIndex) { return text; }
      editable_focused       : editable_focused,
      editable_blur          : editable_blur,
      editable_selectAll     : editable_selectAll,
      editable_wrapContent   : '<div>',       // wrap all editable cell content... makes this widget work in IE, and with autocomplete
      editable_trimContent   : true,          // trim content ( removes outer tabs & carriage returns )
      editable_noEdit        : 'no-edit',     // class name of cell that is not editable
      editable_editComplete  : 'editComplete' // event fired after the table content has been edited
    }
  })
//  // config event variable new in v2.17.6
// .children('tbody').on('editComplete', 'td', editCell)
// .bind('sortBegin sortEnd', sort_start_end)
// .bind('filterStart filterEnd', filter_start_end)
// ('.toggle').click(tog);
// ('[data-search]').click(dataSearch);
};

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// AUX FUNCTIONS
///////////////////////////////////////////////////////////////////////////////////////////////////////////
function ReadCollection(coll_name_path) {
  // returns a promise
  //var coll_name_path = this.getAttribute("coll_name_path");
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  var data = { "coll_name_path": coll_name_path };
  console.log(data)
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/ReadCollection/",
      method: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json',
      success: result => {
        resolve(result); // Resolve the promise with the result
        // Toggle some button colours and functionality
        if (!result.includes("No data")) {
          var EditTableButton = $('#EditTableButton');
          var ExportTableButton = $('#ExportTableButton');
          EditTableButton.css('background-color', EditButtonOn ? grey : blue);
          ExportTableButton.css('background-color', EditButtonOn ? grey : blue);
        }
      },
      error: (xhr, status, error) => {
        reject(error); // Reject the promise with the error
      }
    });
  });
};

var DeleteCollection = function () {
  let coll_name_path = $('#table_title').html();
  coll_name_path = MakeColNamePathPretty(coll_name_path)

  console.log(": ", coll_name_path);
  let confirm = window.confirm("Are you sure you want to delete ".concat(coll_name_path).concat(" ?"));
  if (confirm) {
    $.ajax({
      type: "POST",
      url: "/DeleteCollection/".concat(coll_name_path),
      success: function(response) {
        console.log('Response:', response);
        location.reload() 
      },
      error: function(error) {
        // Handle any errors that occur during the request
        console.log('Error:', error);
      }
    })
  };
};

function exportTable2CSV(coll_name_path, data){
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  $.ajax({
    type: "POST",
    contentType: 'charset=UTF-8',
    url: "/ExportTable/",
    contentType: 'application/json',
    data: JSON.stringify(data),
    success: function(response) {
      $("#CSVExportTable").remove();
      setTimeout( function() {
          console.log(response)
          $("#DBTableNav").append(response);
        }, 50
      )
    },
    error: function(error) {
      // Handle any errors that occur during the request
      console.log(error);
    }
  });
};

function CreateEntry(coll_name_path, data){
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  console.log("CreateEntry: ", coll_name_path);
  $.ajax({
    type: "POST",
    contentType: 'charset=UTF-8',
    url: "/CreateEntry/".concat(coll_name_path),
    data: JSON.stringify(data),
    success: function(response) {
      console.log(response);
    },
      error: function(error) {
      // Handle any errors that occur during the request
      console.log(error);
    }
  });
};

function UpdateEntry(coll_name_path, data){
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  console.log("UpdateEntry: ", coll_name_path);
  $.ajax({
    type: "POST",
    contentType: 'charset=UTF-8',
    url: "/UpdateEntry/".concat(coll_name_path),
    data: JSON.stringify(data),
    success: function(response) {
      console.log(response);
    },
      error: function(error) {
      // Handle any errors that occur during the request
      console.log(error);
    }
  });
};

function DeleteEntry(coll_name_path, ids){
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  console.log("DeleteEntry: ", coll_name_path);
  $.ajax({
    type: "POST",
    contentType: 'charset=UTF-8',
    url: "/DeleteEntry/".concat(coll_name_path),
    data: JSON.stringify(ids),
    success: function(response) {
      console.log(response);
    },
      error: function(error) {
      // Handle any errors that occur during the request
      console.log(error);
    }
  });
};

function MakeColNamePathPretty(coll_name_path){
  return coll_name_path.replace(/ /g, "_").replace(/\//g, ".");
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// AUX FUNCTIONS
///////////////////////////////////////////////////////////////////////////////////////////////////////////
var SwapButtonState = function (){
  AddRowButtonOn = !EditButtonOn
  AddFieldButtonOn = !EditButtonOn
  SaveTableButtonOn = !EditButtonOn
  DeleteAllButtonOn = !EditButtonOn
  EditButtonOn = !EditButtonOn
};

var nTableColumns = function() {
  //Get number of td elements i.e. columns in the table in the DOM
  let row = $('#main_table tr:first').html()
  ans = n_td_elements = row.split("<th").length -1
  console.log(ans);
  return ans
};

var IfTablePresent = function(callback) {

  let table = $('#main_table');
  // If there is a table present in the DOM
  if (table.html()) {
    callback();
  } else {
    console.log("No table present");
  }
};

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// DOM element functions
///////////////////////////////////////////////////////////////////////////////////////////////////////////
var AddRowButtonClick = function () {
  if (AddRowButtonOn) {
    // https://mottie.github.io/tablesorter/docs/example-add-rows.html
    // 
    let deletebutton = '<td><button type="button" class="RemoveRowButton delete-button" title="Remove this row"></button></td>'
    let emptylastrow = '<td><div contenteditable="true"></div></td>'.repeat(nTableColumns()-1)
    // Put into table
    emptylastrow = '<tr>'.concat(deletebutton).concat(emptylastrow).concat('</tr>'),
    $emptylastrow = $(emptylastrow),
    resort = true;
    $('#main_table')
      .find('tbody').append($emptylastrow)
      .trigger('addRows', [$emptylastrow, resort]);
  }
  return false
};

var AddFieldButtonClick = function () {
  if (AddFieldButtonOn) {
    console.log("AddFieldButtonClick")
  }
  return false
};

var DeleteAllButtonClick = function() {
  if (DeleteAllButtonOn){
    console.log("DeleteAllButtonClick")  
    DeleteCollection()
  }
};

var CreateTable = function(coll_name_path) {
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  // Send AJAX request to ReadCollection() in server.py
  ReadCollection(coll_name_path).then((response) => {
    // Insert HTML into DOM
    $('#table_container').html(response);
    let table = $('#main_table');
    // Format table acc. table sorter
    tableSorterInit(table);
    // Insert Title into heading
    let coll_name_path = $('table[class*=dataframe]').attr('coll_name_path');
    coll_name_path = MakeColNamePathPretty(coll_name_path)

    $('#table_title').html(coll_name_path);
    return table
  });
};

var ExportTableButtonClick = function() {
  //data = $('#table_container tbody').html();
  let coll_name_path = $('#table_title').html();
  coll_name_path = MakeColNamePathPretty(coll_name_path)

  // Extract table
  var data = $('#table_container').html();
  // Make it a jquery object
  var $tableData = $('<div>' + data + '</div>');
  // Remove rows where filtered in the class tags
  $tableData.find('tr.filtered').remove();
  modifiedData = $tableData.html()
  modifiedData = modifiedData.replace(/^\s*[\r\n]/gm, '');
  
 exportTable2CSV(coll_name_path, modifiedData);
};

var EditTableButtonClick = function () {
  
  let table = $('#main_table');
  let table_title = $('#table_title').html()
  let editable_columns = Array.from(Array(nTableColumns() - 4).keys(), num => num + 1)

  var toggle_button = $('.toggle');
  var toggle_buttonO = $('.toggle_opposite');
  toggle_button.css('background-color', EditButtonOn ? 'LightGray' : '#06d4df');
  toggle_buttonO.css('background-color', EditButtonOn ? 'DimGray' : 'LightGray');

  // Swap editable everytime clicked
  SwapButtonState()
  if (EditButtonOn) {
    // Make all but the last 3 table columns editable
    // The server ensures these are Created, Modified and _id
    table[0].config.widgetOptions.editable_columns = editable_columns
    table.trigger("updateAll").trigger("applyWidgets");
  } else {
    // Not ideal to just recreate the table but updating widget 
    // options is only allowed once
    CreateTable(table_title)
  }
  return false
};

var CollectionLinkClick = function() {
  //Get var from click and pass into table
  let coll_name_path = this.getAttribute("coll_name_path")
  coll_name_path = MakeColNamePathPretty(coll_name_path)

  CreateTable(coll_name_path)
  if (EditButtonOn) {
    var toggle_button = $('.toggle');
    var toggle_buttonO = $('.toggle_opposite');
    toggle_button.css('background-color', EditButtonOn ? 'LightGray' : '#06d4df');
    toggle_buttonO.css('background-color', EditButtonOn ? 'DimGray' : 'LightGray');
    SwapButtonState()
  }
  return false
};

var SaveTableButtonClick = function() {
  if (SaveTableButtonOn){
    let coll_name_path = $('#table_title').html();
    coll_name_path = MakeColNamePathPretty(coll_name_path)

    let data = $('#table_container').html();
    // Some of the data will be updates to previous entries
    // others might be new e.g. with a new row
    // The serve identifies these and handles separately
    UpdateEntry(coll_name_path, data);
    CreateEntry(coll_name_path, data);
    if (deleted_id_list.length > 0){
      DeleteEntry(coll_name_path, deleted_id_list);
      deleted_id_list.length = 0
    };
   let confirm = window.confirm("Table saved.");

  }
  return false
};

var DisplayCollectionButtonClick = function(){
  let coll_name_path = $('#FindCollectioninput').val();
  coll_name_path = MakeColNamePathPretty(coll_name_path)
  CreateTable(coll_name_path);
};

var RemoveRowButtonClick = function() {
  if (EditButtonOn) {
    let table = $('table');
    let id = $(this).closest('tr').find('td:last').html();
    deleted_id_list.push(id)
    $(this).closest('tr').remove();
    table.trigger('update');
  }
  return false
};

var MakeFirstulTreeClass = function(){
  // Necessary for styling - see _directory-tree.scss
  const divDBDirTree = document.getElementById("DBDirTree");
  // Check if the div exists and has a next sibling
  if (divDBDirTree && divDBDirTree.nextElementSibling) {
    // Find the first ul tag after the div
    const firstULAfterDiv = divDBDirTree.firstChild;
    // Check if the ul tag exists
    if (firstULAfterDiv) {
      // Add a class to the ul tag
      firstULAfterDiv.classList.add("tree");
    }
  }
};

///////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAIN
///////////////////////////////////////////////////////////////////////////////////////////////////////////
$(document).on('click', '#DisplayCollectionButton', DisplayCollectionButtonClick);
$(document).on('click', '#DeleteCollectionButton', DeleteCollection);
$(document).on('click', '.collection_link', CollectionLinkClick);
$(document).on('click', '#EditTableButton', function() {IfTablePresent(EditTableButtonClick);});
$(document).on('click', '#AddRowButton', AddRowButtonClick);
$(document).on('click', '#SaveTableButton', SaveTableButtonClick);
$(document).on('click', '#DeleteAllButton', DeleteAllButtonClick);
$(document).on('click', '#ExportTableButton', function() {IfTablePresent(ExportTableButtonClick);});
$(document).on('click', '.RemoveRowButton', RemoveRowButtonClick);
$(document).ready(MakeFirstulTreeClass);