import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 600
    page.window.height = 600

    db_conn = init_db()

    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.LIGHT
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        theme_switch.label = (
            "Dark theme" if page.theme_mode == ft.ThemeMode.LIGHT else "Light theme"
        )
        page.update()

    page.theme_mode = ft.ThemeMode.LIGHT
    theme_switch = ft.Switch(label="Dark theme", on_change=theme_changed)


    name_input = ft.TextField(label="Name", expand=True)
    phone_input = ft.TextField(label="Phone", expand=True)
    email_input = ft.TextField(label="Email", expand=True)

    inputs = (name_input, phone_input, email_input)

    search_field = ft.TextField(
        hint_text="Search contacts...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value),
        expand=True,
    )

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.Icons.ADD,
        color=ft.Colors.GREY_700,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.padding.symmetric(horizontal=30, vertical=5),
        ),
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Contact Book", size=22, weight=ft.FontWeight.BOLD, expand=True),
                            theme_switch,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                    name_input,
                    phone_input,
                    email_input,
                    ft.Row(
                        [add_button],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Divider(),
                    ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                    search_field,
                    contacts_list_view,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                expand=True,
            ),
            padding=10,
            expand=True,
        )
    )
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)