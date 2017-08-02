/*---------------------------------------------------------
 * OpenERP web_wysiwyg
 *---------------------------------------------------------*/

// currently the WYSIWYG mode is off
var wysiwyg_on = false;

var clicks;

// function which will save the content of the WYSIWYGs into the textareas
var handler = function(){
	if(wysiwyg_on){
		$('textarea').trigger('change');
	
		// Change the css of the openERP translation button
		$('.openerp .oe_input_icon').css({'margin' : '3px 0 0 -21px', 'float' : 'none'});

		// Here we transform all the WYSIWYG textareas into regular textareas
		$('textarea').each(function(){
			try {
				$(this).ckeditorGet().destroy();
			}
			catch(e) { }
		});

		// Remove onclick event on save button.
		$('button.oe_form_button_save, button.oe_selectcreatepopup-form-save, button.oe_selectcreatepopup-form-save-new').unbind('click', handler);

		// currently the WYSIWYG mode is off
		$('.wysiwyg_button').addClass('wysiwyg_button_off');
		$('.wysiwyg_button').text('WYSIWYG on');
		wysiwyg_on = false;
	}else{
		return true;
	}
}

// Triggered when you click on the button WYSIWYG
function toggle_ckeditor(){
	// If the WYSIWYG mode is off
	if(!wysiwyg_on){
		// Here we transform all the regular textareas into WYSIWYG textareas
		$('textarea.field_text_WYSIWYG').ckeditor({ toolbar : 'Mine' });

		// Change the css of the openERP translation button
		$('textarea.field_text_WYSIWYG').next('.oe_input_icon').css({'margin' : '-260px 0 0 -21px', 'float' : 'right'});

		// Add onclick event on save button.
		$('button.oe_form_button_save, button.oe_selectcreatepopup-form-save, button.oe_selectcreatepopup-form-save-new').prependEvent('click', handler);

		// currently the WYSIWYG mode is on
		$('.wysiwyg_button').removeClass('wysiwyg_button_off');
		$('.wysiwyg_button').text('WYSIWYG off');
		wysiwyg_on = true;


	}else{
		// Change the css of the openERP translation button
		$('.openerp .oe_input_icon').css({'margin' : '3px 0 0 -21px', 'float' : 'none'});

		// Here we transform all the WYSIWYG textareas into regular textareas
		$('textarea').each(function(){
			try {
				$(this).ckeditorGet().destroy();
			}
			catch(e) { }
		});

		// Remove onclick event on save button.
		$('button.oe_form_button_save, button.oe_selectcreatepopup-form-save, button.oe_selectcreatepopup-form-save-new').unbind('click', handler);

		// currently the WYSIWYG mode is off
		$('.wysiwyg_button').addClass('wysiwyg_button_off');
		$('.wysiwyg_button').text('WYSIWYG on');
		wysiwyg_on = false;
	}
}

// vim:et fdc=0 fdl=0:
