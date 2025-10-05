import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db


def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in the ListView with filter if search term is provided."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contact_card = ft.Card(
            elevation=3,
            margin=5,
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            [
                                ft.Text(name, size=18, weight=ft.FontWeight.BOLD, expand=True),
                                ft.PopupMenuButton(
                                    icon=ft.Icons.MORE_VERT,
                                    items=[
                                        ft.PopupMenuItem(
                                            text="Edit",
                                            icon=ft.Icons.EDIT,
                                            on_click=lambda _, c=contact: open_edit_dialog(
                                                page, c, db_conn, contacts_list_view
                                            ),
                                        ),
                                        ft.PopupMenuItem(),
                                        ft.PopupMenuItem(
                                            text="Delete",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda _, cid=contact_id: delete_contact(
                                                page, cid, db_conn, contacts_list_view
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.PHONE, color=ft.Colors.BLUE),
                                ft.Text(phone if phone else "No phone", size=14),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.Icons.EMAIL, color=ft.Colors.GREEN),
                                ft.Text(email if email else "No email", size=14),
                            ]
                        ),
                    ],
                ),
            ),
        )

        contacts_list_view.controls.append(contact_card)

    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs

    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    else:
        name_input.error_text = None

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()


def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Ask for confirmation before deleting a contact and refreshes the list."""
    def on_yes_click(e):
        delete_contact_db(db_conn, contact_id)
        page.close(confirm_dialog)
        display_contacts(page, contacts_list_view, db_conn)
        page.update()
    
    def on_no_click(e):
        page.close(confirm_dialog)
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Confirmation", text_align=ft.TextAlign.CENTER),
        content=ft.Text("Are you sure you want to delete this contact?", text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        actions=[
            ft.TextButton("No", on_click=on_no_click, 
                          style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREY,shape=ft.RoundedRectangleBorder(radius=5)),
                          ),
            ft.TextButton("Yes", on_click=on_yes_click, 
                          style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED, shape=ft.RoundedRectangleBorder(radius=5)),
                          ),
        ],
        icon=ft.Icon(name=ft.Icons.WARNING, color=ft.Colors.RED),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.open(confirm_dialog)
    page.update()



def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
                content=ft.Container(
            content=ft.Column(
                    controls=[edit_name, edit_phone, edit_email],
                    tight=True,          
                    spacing=10,          
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=10,
                width=300,            
            ),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=lambda e: setattr(dialog, "open", False) or page.update(),
            ),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )

    page.open(dialog)
