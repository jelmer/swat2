<%namespace name="base" file="/default/base/base.mako" />
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>${self.page_title()}</title>
	${base.head_tags()}
    </head>
    
    <body>
	<div class="swat-content login round-2px">            
	    ${base.samba_logo(False)}
	    
	    <p class="message">${_('Login into the Samba Web Administration Tool')}</p>
		 
	    ${login_form()}
	    
	    <ul class="useful-links">
		<li><a href="#">${_('get help!')}</a></li>
		<li><a href="#">${_('about')}</a></li>
	    </ul>
	</div>
</html>

<%def name="page_title()">
    ${_('Samba Web Administration Tool')}
</%def>

<%def name="login_form()">    
    ${h.form(h.url_for(controller='authentication', action='do'), method='post', id='form-login', class_='login')}
	<ol>
	    <li>
		<label title="${_("Type your Username. Typically 'root'")}" for="form-login-username">${_('Username')}:</label>
		${h.text('login-username', '', id = 'form-login-username', class_='round-2px')}
	    </li>
	    <li>
		<label title="${_("Type the Password for the user you chose above")}" for="form-login-password">${_('Password')}:</label>
		${h.password('login-password', '', id = 'form-login-password', class_='round-2px')}
	    </li>
	    
	    <li class="submission">
		${h.submit('login-password', value=_('Login'), class_='round-2px')}
	    </li>
	</ol>
    ${h.end_form()}
    
    <!--
    
        ${h.form(h.url_for(controller='dashboard', action='goto'), method='get')}
	<div class="filter-items">
	    <label title="${_('Go directly to...')}" for="goto-items-textbox">${_('Goto')}: </label>
	    ${h.text('where', '', id = 'goto-items-textbox')}
	</div>
    ${h.end_form()}
    
    -->
    
</%def>
	