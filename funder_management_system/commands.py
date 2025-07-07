import click
import frappe
from frappe.commands import get_site, pass_context
from frappe.exceptions import SiteNotSpecifiedError


@click.command("setup-email-account")
@click.option("--interactive", "-i", is_flag=True, default=True, help="Interactive mode to set up email account")
@pass_context
def setup_email_account(context, interactive=True):
	"""Set up a new Email Account interactively"""
	
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		if interactive:
			_interactive_email_account_setup()
		else:
			click.echo("Non-interactive mode not implemented. Use --interactive flag.")
	finally:
		frappe.destroy()


def _show_gmail_app_password_instructions():
	"""Display instructions for generating Gmail App Password"""
	click.echo("\n" + "="*70)
	click.echo(click.style("Gmail App Password Setup Instructions", fg="yellow", bold=True))
	click.echo("="*70)
	click.echo("\nTo use Gmail with IMAP, you need to generate an App Password. Follow these steps:")
	
	click.echo("\n1. Enable 2-Step Verification (if not already enabled):")
	click.echo("   • Visit: https://myaccount.google.com/security")
	click.echo("   • Click on '2-Step Verification'")
	click.echo("   • Follow the steps to enable it")
	
	click.echo("\n2. Generate App Password:")
	click.echo("   • Visit: https://myaccount.google.com/apppasswords")
	click.echo("   • Select 'Mail' from the app dropdown")
	click.echo("   • Select your device type")
	click.echo("   • Click 'Generate'")
	click.echo("   • Google will display a 16-character password")
	click.echo("   • Copy this password - you'll need it in the next step")
	
	click.echo("\n" + click.style("Important Notes:", fg="yellow", bold=True))
	click.echo("• Use this App Password instead of your regular Gmail password")
	click.echo("• The App Password is 16 characters without spaces")
	click.echo("• You only see the App Password once, so copy it carefully")
	click.echo("• Each App Password can only be used for one specific app/device")
	
	click.echo("\n" + "="*70)
	if not click.confirm("Have you generated your App Password?", default=False):
		if click.confirm("Would you like to open the App Passwords page in your browser?", default=True):
			click.launch("https://myaccount.google.com/apppasswords")
		click.echo("\nPlease generate the App Password before continuing.")
		if not click.confirm("Continue with setup?", default=True):
			raise click.Abort()


def _interactive_email_account_setup():
	"""Interactive function to gather email account details and create the record"""
	
	click.echo("\n" + "="*70)
	click.echo("Welcome to Email Account Setup Wizard")
	click.echo("="*70)
	click.echo("This wizard will help you configure a new email account for your site.")
	click.echo("Please provide the following information:\n")
	
	# Basic Account Information
	click.echo("Basic Account Information:")
	click.echo("-" * 35)
	
	email_id = click.prompt(
		click.style("Email Address", fg="cyan", bold=True),
		type=str
	).strip().lower()
	
	# Validate email format
	if "@" not in email_id or "." not in email_id.split("@")[1]:
		click.echo(click.style("Warning: Email format seems invalid", fg="yellow"))
		if not click.confirm("Continue anyway?", default=False):
			click.echo("Setup cancelled.")
			return
	
	email_account_name = click.prompt(
		click.style("Account Name (e.g., 'Support', 'Sales')", fg="cyan", bold=True),
		type=str,
		default=email_id.split("@")[0].title()
	).strip()
	
	# Service Selection
	click.echo(f"\nEmail Service Configuration:")
	click.echo("-" * 35)
	
	service_options = ["GMail", "Outlook.com", "Yahoo Mail", "Custom"]
	click.echo("Available services:")
	for i, service in enumerate(service_options, 1):
		click.echo(f"  {i}. {service}")
	
	service_choice = click.prompt(
		click.style("Select service", fg="cyan"),
		type=click.IntRange(1, len(service_options)),
		default=1
	)
	
	service = service_options[service_choice - 1] if service_choice <= 3 else ""
	
	# Show Gmail App Password instructions if Gmail is selected
	if service == "GMail":
		_show_gmail_app_password_instructions()
	
	# Authentication Method
	click.echo(f"\nAuthentication Method:")
	click.echo("-" * 25)
	
	auth_methods = ["Basic (Username/Password)", "OAuth (Recommended for Gmail/Outlook)"]
	click.echo("Available authentication methods:")
	for i, method in enumerate(auth_methods, 1):
		click.echo(f"  {i}. {method}")
	
	auth_choice = click.prompt(
		click.style("Select authentication method", fg="cyan"),
		type=click.IntRange(1, 2),
		default=1
	)
	
	auth_method = "Basic" if auth_choice == 1 else "OAuth"
	password = None
	
	if auth_method == "Basic":
		password_prompt = "App Password" if service == "GMail" else "Password"
		password = click.prompt(
			click.style(password_prompt, fg="yellow"),
			type=str,
			hide_input=True
		)
		
		if service == "GMail" and len(password.replace(" ", "")) != 16:
			click.echo(click.style("\nWarning: Gmail App Passwords are 16 characters long.", fg="yellow"))
			if not click.confirm("Continue anyway?", default=False):
				click.echo("Setup cancelled.")
				return
	
	# Email Features
	click.echo(f"\nEmail Features:")
	click.echo("-" * 20)
	
	enable_incoming = click.confirm(
		click.style("Enable incoming emails (receiving)?", fg="cyan"),
		default=False
	)
	
	enable_outgoing = click.confirm(
		click.style("Enable outgoing emails (sending)?", fg="cyan"),
		default=True
	)
	
	default_incoming = False
	default_outgoing = False
	
	if enable_incoming:
		default_incoming = click.confirm(
			click.style("Set as default incoming account?", fg="yellow"),
			default=False
		)
	
	if enable_outgoing:
		default_outgoing = click.confirm(
			click.style("Set as default outgoing account?", fg="yellow"),
			default=False
		)
	
	# Advanced Settings (only for custom service)
	email_server = None
	smtp_server = None
	incoming_port = None
	smtp_port = None
	use_ssl = True
	use_tls = True
	use_imap = True
	
	if not service:  # Custom service
		click.echo(f"\nCustom Server Configuration:")
		click.echo("-" * 32)
		
		if enable_incoming:
			use_imap = click.confirm(
				click.style("Use IMAP (recommended over POP3)?", fg="cyan"),
				default=True
			)
			
			email_server = click.prompt(
				click.style("Incoming server (e.g., imap.gmail.com)", fg="cyan"),
				type=str
			).strip()
			
			incoming_port = click.prompt(
				click.style("Incoming port (993 for IMAP SSL, 143 for IMAP)", fg="cyan"),
				type=int,
				default=993 if use_imap else 995
			)
			
			use_ssl = click.confirm(
				click.style("Use SSL for incoming?", fg="cyan"),
				default=True
			)
		
		if enable_outgoing:
			smtp_server = click.prompt(
				click.style("Outgoing server (e.g., smtp.gmail.com)", fg="cyan"),
				type=str
			).strip()
			
			smtp_port = click.prompt(
				click.style("Outgoing port (587 for TLS, 465 for SSL)", fg="cyan"),
				type=int,
				default=587
			)
			
			use_tls = click.confirm(
				click.style("Use TLS for outgoing?", fg="cyan"),
				default=True
			)
	
	# Optional Settings
	click.echo(f"\nOptional Settings:")
	click.echo("-" * 20)
	
	track_email_status = click.confirm(
		click.style("Track email status (opens, clicks)?", fg="yellow"),
		default=True
	)
	
	add_signature = click.confirm(
		click.style("Add email signature?", fg="yellow"),
		default=False
	)
	
	signature = None
	if add_signature:
		signature = click.prompt(
			click.style("Email signature", fg="yellow"),
			type=str,
			default=f"Best regards,\n{email_account_name}"
		)
	
	# Display Summary
	click.echo("\n" + "="*70)
	click.echo("Email Account Configuration Summary")
	click.echo("="*70)
	click.echo(f"Email Address: {click.style(email_id, fg='green', bold=True)}")
	click.echo(f"Account Name: {click.style(email_account_name, fg='green', bold=True)}")
	click.echo(f"Service: {click.style(service or 'Custom', fg='green')}")
	click.echo(f"Authentication: {click.style(auth_method, fg='green')}")
	click.echo(f"Incoming Enabled: {click.style('Yes' if enable_incoming else 'No', fg='green' if enable_incoming else 'red')}")
	click.echo(f"Outgoing Enabled: {click.style('Yes' if enable_outgoing else 'No', fg='green' if enable_outgoing else 'red')}")
	
	if default_incoming:
		click.echo(f"Default Incoming: {click.style('Yes', fg='green', bold=True)}")
	if default_outgoing:
		click.echo(f"Default Outgoing: {click.style('Yes', fg='green', bold=True)}")
	
	if not service:
		if email_server:
			click.echo(f"Incoming Server: {click.style(email_server + ':' + str(incoming_port), fg='green')}")
		if smtp_server:
			click.echo(f"Outgoing Server: {click.style(smtp_server + ':' + str(smtp_port), fg='green')}")
	
	click.echo("="*70)
	
	# Confirm creation
	if click.confirm(f"\nCreate this email account?", default=True):
		try:
			# Check if email account already exists
			if frappe.db.exists("Email Account", {"email_id": email_id}):
				click.echo(click.style(f"Email account '{email_id}' already exists!", fg="red"))
				return
			
			if frappe.db.exists("Email Account", {"email_account_name": email_account_name}):
				click.echo(click.style(f"Account name '{email_account_name}' already exists!", fg="red"))
				return
			
			# Prepare document data
			doc_data = {
				"doctype": "Email Account",
				"email_id": email_id,
				"email_account_name": email_account_name,
				"auth_method": auth_method,
				"enable_incoming": enable_incoming,
				"enable_outgoing": enable_outgoing,
				"default_incoming": default_incoming,
				"default_outgoing": default_outgoing,
				"track_email_status": track_email_status
			}
			
			# Add service if selected
			if service:
				doc_data["service"] = service
			
			# Add password for basic auth
			if auth_method == "Basic" and password:
				doc_data["password"] = password
			
			# Add incoming settings
			if enable_incoming:
				doc_data["use_imap"] = use_imap
				
				# Set server configurations based on service
				if service == "GMail":
					doc_data["email_server"] = "imap.gmail.com"
					doc_data["incoming_port"] = "993"
					doc_data["use_ssl"] = True
				elif service == "Outlook.com":
					doc_data["email_server"] = "outlook.office365.com"
					doc_data["incoming_port"] = "993"
					doc_data["use_ssl"] = True
				elif service == "Yahoo Mail":
					doc_data["email_server"] = "imap.mail.yahoo.com"
					doc_data["incoming_port"] = "993"
					doc_data["use_ssl"] = True
				elif email_server:  # Custom service
					doc_data["email_server"] = email_server
					if incoming_port:
						doc_data["incoming_port"] = str(incoming_port)
					doc_data["use_ssl"] = use_ssl
			
			# Add outgoing settings
			if enable_outgoing:
				# Set SMTP server configurations based on service
				if service == "GMail":
					doc_data["smtp_server"] = "smtp.gmail.com"
					doc_data["smtp_port"] = "587"
					doc_data["use_tls"] = True
				elif service == "Outlook.com":
					doc_data["smtp_server"] = "smtp-mail.outlook.com"
					doc_data["smtp_port"] = "587"
					doc_data["use_tls"] = True
				elif service == "Yahoo Mail":
					doc_data["smtp_server"] = "smtp.mail.yahoo.com"
					doc_data["smtp_port"] = "587"
					doc_data["use_tls"] = True
				elif smtp_server:  # Custom service
					doc_data["smtp_server"] = smtp_server
					if smtp_port:
						doc_data["smtp_port"] = str(smtp_port)
					doc_data["use_tls"] = use_tls
			
			# Add signature
			if add_signature and signature:
				doc_data["add_signature"] = True
				doc_data["signature"] = signature
			
			# Create the document
			email_account_doc = frappe.get_doc(doc_data)
			
			# Add default IMAP folder for IMAP accounts after document creation
			if enable_incoming and use_imap:
				email_account_doc.append("imap_folder", {
					"folder_name": "INBOX",
					"append_to": "",
					"use_for_syncing": 1
				})
			
			email_account_doc.insert()
			frappe.db.commit()
			
			click.echo(f"\n{click.style('Success!', fg='green', bold=True)} Email account created successfully!")
			click.echo(f"Account Name: {click.style(email_account_doc.name, fg='cyan', bold=True)}")
			click.echo(f"You can view it at: {click.style(f'/app/email-account/{email_account_doc.name}', fg='blue')}")
			
			# Additional setup notes
			if auth_method == "OAuth":
				click.echo(f"\n{click.style('Next Steps for OAuth:', fg='yellow', bold=True)}")
				click.echo("1. Set up a Connected App in your site")
				click.echo("2. Configure OAuth credentials with your email provider")
				click.echo("3. Authorize the connection in the Email Account form")
			
			if service in ["GMail", "Outlook.com"]:
				click.echo(f"\n{click.style('Provider-specific Notes:', fg='blue', bold=True)}")
				if service == "GMail":
					click.echo("• For Gmail, consider using App Passwords if using Basic auth")
					click.echo("• OAuth is recommended for better security")
				elif service == "Outlook.com":
					click.echo("• Modern authentication (OAuth) is preferred")
					click.echo("• Basic auth may require enabling legacy authentication")
			
		except Exception as e:
			frappe.db.rollback()
			click.echo(f"\n{click.style('Error creating email account:', fg='red')} {str(e)}")
			click.echo("Please check your inputs and try again.")
	else:
		click.echo("\nEmail account setup cancelled.")


@click.command("list-email-accounts")
@click.option("--limit", default=20, help="Number of email accounts to display")
@click.option("--format", default="table", type=click.Choice(["table", "json"]), help="Output format")
@pass_context
def list_email_accounts(context, limit, format):
	"""List existing Email Account records"""
	
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		email_accounts = frappe.get_all(
			"Email Account",
			fields=["name", "email_id", "email_account_name", "service", "enable_incoming", 
					"enable_outgoing", "default_incoming", "default_outgoing", "creation"],
			order_by="creation desc",
			limit=limit
		)
		
		if not email_accounts:
			click.echo("No email accounts found.")
			return
		
		if format == "json":
			import json
			click.echo(json.dumps(email_accounts, indent=2, default=str))
		else:
			# Table format
			click.echo(f"\n{click.style('Email Accounts', fg='cyan', bold=True)} (Last {len(email_accounts)} records)")
			click.echo("="*120)
			click.echo(f"{'Account Name':<20} {'Email':<30} {'Service':<15} {'In':<3} {'Out':<3} {'Def In':<6} {'Def Out':<7} {'Created':<12}")
			click.echo("-"*120)
			
			for acc in email_accounts:
				created_date = acc.creation.strftime("%Y-%m-%d") if acc.creation else "N/A"
				in_enabled = "Yes" if acc.enable_incoming else "No"
				out_enabled = "Yes" if acc.enable_outgoing else "No"
				def_in = "Yes" if acc.default_incoming else "No"
				def_out = "Yes" if acc.default_outgoing else "No"
				
				click.echo(f"{acc.email_account_name[:19]:<20} {acc.email_id[:29]:<30} {(acc.service or 'Custom')[:14]:<15} {in_enabled:<3} {out_enabled:<3} {def_in:<6} {def_out:<7} {created_date:<12}")
			
			click.echo("="*120)
			click.echo(f"Total: {len(email_accounts)} email account(s)")
			click.echo("Legend: In=Incoming, Out=Outgoing, Def=Default")
			
	finally:
		frappe.destroy()


@click.command("create-user")
@pass_context
def create_user(context):
	"""Create a new Frappe user with specific roles"""
	
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		# Basic user information
		click.echo("\n" + "="*50)
		click.echo("Create New User")
		click.echo("="*50)
		
		# Get user details
		first_name = click.prompt(
			click.style("First Name", fg="cyan", bold=True),
			type=str
		).strip()
		
		last_name = click.prompt(
			click.style("Last Name", fg="cyan", bold=True),
			type=str
		).strip()
		
		email = click.prompt(
			click.style("Email", fg="cyan", bold=True),
			type=str
		).strip().lower()
		
		# Validate email format
		if "@" not in email or "." not in email.split("@")[1]:
			click.echo(click.style("Error: Invalid email format", fg="red"))
			return
		
		# Role selection
		click.echo("\nAvailable Roles:")
		roles = ["Fundraising Admin"]
		for idx, role in enumerate(roles, 1):
			click.echo(f"  {idx}. {role}")
		
		role_choice = click.prompt(
			click.style("\nSelect role", fg="cyan"),
			type=click.IntRange(1, len(roles)),
			default=1
		)
		
		selected_role = roles[role_choice - 1]
		
		# Display summary
		click.echo("\n" + "="*50)
		click.echo("User Details Summary:")
		click.echo("="*50)
		click.echo(f"Name: {click.style(f'{first_name} {last_name}', fg='green')}")
		click.echo(f"Email: {click.style(email, fg='green')}")
		click.echo(f"Role: {click.style(selected_role, fg='green')}")
		
		if not click.confirm("\nCreate user with these details?", default=True):
			click.echo("User creation cancelled.")
			return
		
		# Check if user already exists
		if frappe.db.exists("User", {"email": email}):
			click.echo(click.style(f"\nError: User with email '{email}' already exists!", fg="red"))
			return
		
		# Create user
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
			"send_welcome_email": 1,
			"enabled": 1,
			"is_fundraising_admin": 1,
			"user_type": "System User",
			"roles": [{
				"role": selected_role
			}]
		})
		
		user.insert(ignore_permissions=True)
		frappe.db.commit()
		
		click.echo(click.style("\nSuccess!", fg="green", bold=True))
		click.echo(f"User '{email}' created successfully with role '{selected_role}'")
		click.echo("A welcome email has been sent with login credentials.")
		
	except Exception as e:
		frappe.db.rollback()
		click.echo(click.style("\nError creating user:", fg="red"))
		click.echo(str(e))
	finally:
		frappe.destroy()


@click.command("setup-email-account-cli")
@click.option("--email", required=True, help="Email address")
@click.option("--account-name", required=True, help="Account name (e.g., Support, Sales)")
@click.option("--service", type=click.Choice(["GMail", "Outlook.com", "Yahoo Mail", "Custom"]), default="GMail", help="Email service provider")
@click.option("--password", required=True, help="Password or App Password for the email account")
@click.option("--incoming/--no-incoming", default=True, help="Enable incoming emails")
@click.option("--outgoing/--no-outgoing", default=True, help="Enable outgoing emails")
@click.option("--default-incoming/--no-default-incoming", default=False, help="Set as default incoming account")
@click.option("--default-outgoing/--no-default-outgoing", default=False, help="Set as default outgoing account")
@click.option("--email-signature", default="", help="Email signature")
# Custom server options
@click.option("--imap-server", help="IMAP server (for custom service)")
@click.option("--imap-port", type=int, help="IMAP port (for custom service)")
@click.option("--smtp-server", help="SMTP server (for custom service)")
@click.option("--smtp-port", type=int, help="SMTP port (for custom service)")
@click.option("--use-imap/--use-pop3", default=True, help="Use IMAP or POP3 for incoming")
@click.option("--use-ssl/--no-ssl", default=True, help="Use SSL for incoming")
@click.option("--use-tls/--no-tls", default=True, help="Use TLS for outgoing")
@pass_context
def setup_email_account_cli(context, email, account_name, service, password, incoming, outgoing,
                          default_incoming, default_outgoing, email_signature,
                          imap_server, imap_port, smtp_server, smtp_port,
                          use_imap, use_ssl, use_tls):
    """Set up an email account using command line parameters"""
    
    if not context.sites:
        raise SiteNotSpecifiedError
    
    site = get_site(context)
    frappe.init(site=site)
    frappe.connect()
    
    try:
        # Validate email format
        if "@" not in email or "." not in email.split("@")[1]:
            click.echo(click.style("Error: Invalid email format", fg="red"))
            return
        
        # Check if email account already exists
        if frappe.db.exists("Email Account", {"email_id": email}):
            click.echo(click.style(f"Email account '{email}' already exists!", fg="red"))
            return
        
        if frappe.db.exists("Email Account", {"email_account_name": account_name}):
            click.echo(click.style(f"Account name '{account_name}' already exists!", fg="red"))
            return
        
        # Prepare document data
        doc_data = {
            "doctype": "Email Account",
            "email_id": email,
            "email_account_name": account_name,
            "service": service if service != "Custom" else "",
            "password": password,
            "enable_incoming": incoming,
            "enable_outgoing": outgoing,
            "default_incoming": default_incoming,
            "default_outgoing": default_outgoing,
            "use_imap": use_imap,
            "track_email_status": 1
        }
        
        # Add signature if provided
        if email_signature:
            doc_data.update({
                "add_signature": 1,
                "signature": email_signature
            })
        
        # Add incoming settings
        if incoming:
            if service == "GMail":
                doc_data.update({
                    "email_server": "imap.gmail.com",
                    "incoming_port": "993",
                    "use_ssl": True
                })
            elif service == "Outlook.com":
                doc_data.update({
                    "email_server": "outlook.office365.com",
                    "incoming_port": "993",
                    "use_ssl": True
                })
            elif service == "Yahoo Mail":
                doc_data.update({
                    "email_server": "imap.mail.yahoo.com",
                    "incoming_port": "993",
                    "use_ssl": True
                })
            elif service == "Custom":
                if not imap_server:
                    click.echo(click.style("Error: IMAP server required for custom service", fg="red"))
                    return
                doc_data.update({
                    "email_server": imap_server,
                    "incoming_port": str(imap_port) if imap_port else "993",
                    "use_ssl": use_ssl
                })
        
        # Add outgoing settings
        if outgoing:
            if service == "GMail":
                doc_data.update({
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": "587",
                    "use_tls": True
                })
            elif service == "Outlook.com":
                doc_data.update({
                    "smtp_server": "smtp-mail.outlook.com",
                    "smtp_port": "587",
                    "use_tls": True
                })
            elif service == "Yahoo Mail":
                doc_data.update({
                    "smtp_server": "smtp.mail.yahoo.com",
                    "smtp_port": "587",
                    "use_tls": True
                })
            elif service == "Custom":
                if not smtp_server:
                    click.echo(click.style("Error: SMTP server required for custom service", fg="red"))
                    return
                doc_data.update({
                    "smtp_server": smtp_server,
                    "smtp_port": str(smtp_port) if smtp_port else "587",
                    "use_tls": use_tls
                })
        
        # Create the document
        email_account_doc = frappe.get_doc(doc_data)
        
        # Add default IMAP folder for IMAP accounts
        if incoming and use_imap:
            email_account_doc.append("imap_folder", {
                "folder_name": "INBOX",
                "append_to": "",
                "use_for_syncing": 1
            })
        
        email_account_doc.insert()
        frappe.db.commit()
        
        click.echo(click.style("\nSuccess!", fg="green", bold=True))
        click.echo(f"Email account '{email}' created successfully!")
        
        # Provider-specific notes
        if service == "GMail":
            click.echo("\nNote: For Gmail:")
            click.echo("• Make sure to use an App Password if 2FA is enabled")
            click.echo("• OAuth is recommended for better security")
        elif service == "Outlook.com":
            click.echo("\nNote: For Outlook:")
            click.echo("• Modern authentication (OAuth) is preferred")
            click.echo("• Basic auth may require enabling legacy authentication")
        
    except Exception as e:
        frappe.db.rollback()
        click.echo(click.style("\nError creating email account:", fg="red"))
        click.echo(str(e))
    finally:
        frappe.destroy()


@click.command("create-user-cli")
@click.option("--first-name", required=True, help="User's first name")
@click.option("--last-name", required=True, help="User's last name")
@click.option("--email", required=True, help="User's email address")
@click.option("--role", type=click.Choice(["Fundraising Admin"]), required=True, help="User's role")
@click.option("--send-welcome-email/--no-welcome-email", default=True, help="Send welcome email with credentials")
@pass_context
def create_user_cli(context, first_name, last_name, email, role, send_welcome_email):
	"""Create a new Frappe user with specific role using command line parameters"""
	
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		# Validate email format
		if "@" not in email or "." not in email.split("@")[1]:
			click.echo(click.style("Error: Invalid email format", fg="red"))
			return
		
		# Check if user already exists
		if frappe.db.exists("User", {"email": email}):
			click.echo(click.style(f"\nError: User with email '{email}' already exists!", fg="red"))
			return
		
		# Create user
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
			"send_welcome_email": send_welcome_email,
			"is_fundraising_admin": 1,
			"enabled": 1,
			"user_type": "System User",
			"roles": [{
				"role": role
			}]
		})
		
		user.insert(ignore_permissions=True)
		frappe.db.commit()
		
		click.echo(click.style("\nSuccess!", fg="green", bold=True))
		click.echo(f"User '{email}' created successfully with role '{role}'")
		if send_welcome_email:
			click.echo("A welcome email has been sent with login credentials.")
		
	except Exception as e:
		frappe.db.rollback()
		click.echo(click.style("\nError creating user:", fg="red"))
		click.echo(str(e))
	finally:
		frappe.destroy()


@click.command("list-users")
@click.option("--limit", default=20, help="Number of users to display")
@click.option("--format", default="simple", type=click.Choice(["simple", "json"]), help="Output format")
@pass_context
def list_users(context, limit, format):
	"""List users with their name, email and roles"""
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		# Get users with their roles
		users = frappe.get_all(
			"User",
			fields=["name", "first_name", "last_name", "email", "enabled"],
			filters={"name": ["not in", ["Guest", "Administrator"]]},
			limit=limit
		)
		
		# Get roles for each user
		for user in users:
			roles = frappe.get_all(
				"Has Role",
				fields=["role"],
				filters={"parent": user.name},
				pluck="role"
			)
			user.roles = ", ".join(roles) if roles else "No roles"
			user.full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "Not set"
			user.status = "Active" if user.enabled else "Disabled"
			
			# Remove unnecessary fields
			del user.first_name
			del user.last_name
			del user.enabled
		
		if format == "json":
			import json
			click.echo(json.dumps(users, indent=2))
		else:
			click.echo("\nUser List:")
			click.echo("=" * 80)
			for user in users:
				click.echo(f"\n{click.style(user.full_name, fg='green', bold=True)}")
				click.echo(f"Email: {user.email}")
				click.echo(f"Roles: {user.roles}")
				click.echo(f"Status: {click.style(user.status, fg='blue' if user.status == 'Active' else 'red')}")
				click.echo("-" * 40)
		
		click.echo(f"\nTotal users shown: {len(users)}")
	
	except Exception as e:
		click.echo(f"Error: {str(e)}")
	finally:
		frappe.destroy()


@click.command("make-module-profile")
@click.argument("profile_name", required=True)
@click.argument("allowed_modules", nargs=-1, required=True)
@click.option("--force", is_flag=True, default=False, help="Overwrite if profile already exists")
@pass_context
def make_module_profile(context, profile_name, allowed_modules, force):
	"""Create a new module profile with access to only specified modules.
	All other modules will be blocked.
	
	Example: bench --site sitename make-module-profile "Standard Access" "Budget Planning" "History"
	"""
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		# Check if profile already exists
		if frappe.db.exists("Module Profile", profile_name) and not force:
			click.echo(f"Module Profile '{profile_name}' already exists. Use --force to overwrite.")
			return
		
		# Get list of all available modules
		all_modules = frappe.get_all("Module Def", pluck="name")
		
		# Validate allowed modules
		invalid_modules = [m for m in allowed_modules if m not in all_modules]
		if invalid_modules:
			click.echo(f"Invalid modules: {', '.join(invalid_modules)}")
			click.echo(f"\nAvailable modules:")
			click.echo("\n".join(sorted(all_modules)))
			return
		
		# Get modules to block (all modules except allowed ones)
		modules_to_block = [m for m in all_modules if m not in allowed_modules]
		
		# Create or update module profile
		if frappe.db.exists("Module Profile", profile_name):
			doc = frappe.get_doc("Module Profile", profile_name)
			doc.block_modules = []  # Clear existing modules
		else:
			doc = frappe.get_doc({
				"doctype": "Module Profile",
				"module_profile_name": profile_name,
				"block_modules": []
			})
		
		# Add modules to block
		for module in modules_to_block:
			doc.append("block_modules", {"module": module})
		
		doc.save()
		frappe.db.commit()
		
		# Show success message
		click.echo(f"\nCreated Module Profile: {click.style(profile_name, fg='green')}")
		click.echo(f"\nAllowed Modules:")
		for module in sorted(allowed_modules):
			click.echo(f"  - {click.style(module, fg='green')}")
		
		click.echo(f"\nBlocked Modules:")
		for module in sorted(modules_to_block):
			click.echo(f"  - {click.style(module, fg='yellow')}")
		
	except Exception as e:
		click.echo(f"Error: {str(e)}")
		frappe.db.rollback()
	finally:
		frappe.destroy()


@click.command("make-role-profile")
@click.argument("profile_name", required=True)
@click.argument("roles", nargs=-1, required=True)
@click.option("--force", is_flag=True, default=False, help="Overwrite if profile already exists")
@pass_context
def make_role_profile(context, profile_name, roles, force):
	"""Create a new role profile with specified roles.
	
	Example: bench --site sitename make-role-profile "Standard User" "System Manager" "Report Manager"
	"""
	if not context.sites:
		raise SiteNotSpecifiedError
	
	site = get_site(context)
	frappe.init(site=site)
	frappe.connect()
	
	try:
		# Check if profile already exists
		if frappe.db.exists("Role Profile", profile_name) and not force:
			click.echo(f"Role Profile '{profile_name}' already exists. Use --force to overwrite.")
			return
		
		# Get list of all available roles
		all_roles = frappe.get_all("Role", pluck="name")
		
		# Validate roles
		invalid_roles = [r for r in roles if r not in all_roles]
		if invalid_roles:
			click.echo(f"Invalid roles: {', '.join(invalid_roles)}")
			click.echo(f"\nAvailable roles:")
			click.echo("\n".join(sorted(all_roles)))
			return
		
		# Create or update role profile
		if frappe.db.exists("Role Profile", profile_name):
			doc = frappe.get_doc("Role Profile", profile_name)
			doc.roles = []  # Clear existing roles
		else:
			doc = frappe.get_doc({
				"doctype": "Role Profile",
				"role_profile": profile_name,
				"roles": []
			})
		
		# Add roles
		for role in roles:
			doc.append("roles", {"role": role})
		
		doc.save()
		frappe.db.commit()
		
		# Show success message
		click.echo(f"\nCreated Role Profile: {click.style(profile_name, fg='green')}")
		click.echo(f"\nAssigned Roles:")
		for role in sorted(roles):
			click.echo(f"  - {click.style(role, fg='green')}")
		
	except Exception as e:
		click.echo(f"Error: {str(e)}")
		frappe.db.rollback()
	finally:
		frappe.destroy()


# Register commands
commands = [
	setup_email_account,
	setup_email_account_cli,
	list_email_accounts,
	create_user,
	create_user_cli,
	list_users,
	make_module_profile,
	make_role_profile
] 
