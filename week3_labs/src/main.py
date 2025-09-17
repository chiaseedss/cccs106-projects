import flet as ft
import mysql.connector
from db_connection import connect_db


def main(page: ft.Page):
    page.window.title_bar_hidden = True
    page.window.frameless = True
    page.title = "User Login"
    page.window.alignment = ft.alignment.center
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT

    login_title = ft.Text("User Login", 
                          text_align=ft.TextAlign.CENTER,
                          size=20,
                          weight=ft.FontWeight.BOLD,
                          font_family="Arial")

    username = ft.TextField(label="User name",
                            hint_text="Enter your user name",
                            helper_text="This is your unique identifier",
                            width=300, 
                            autofocus=True, 
                            icon=ft.Icons.PERSON,
                            fill_color=ft.Colors.LIGHT_BLUE_ACCENT)

    password = ft.TextField(label="Password",
                            hint_text="Enter your password",
                            helper_text="This is your secret key",
                            width=300, 
                            autofocus=True, 
                            password=True, 
                            can_reveal_password=True,
                            icon=ft.Icons.PASSWORD,
                            fill_color=ft.Colors.LIGHT_BLUE_ACCENT)
    
    def login_click(e):
        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful", text_align=ft.TextAlign.CENTER),
            content=ft.Text(f"Welcome, {username.value}!", text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))
            ],
            icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
        )

        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))
            ],
            icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
        )

        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
            icon=ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE),
        )

        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error", text_align=ft.TextAlign.CENTER),
            content=ft.Text("An error occurred while connecting to the database", text_align=ft.TextAlign.CENTER),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))],
        )

        if not username.value or not password.value:
            page.open(invalid_input_dialog)
            page.update()
            return
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username.value, password.value),
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)

        except mysql.connector.Error:
            page.open(database_error_dialog)
        
        page.update()

    login_button = ft.ElevatedButton(
        text="Login",
        icon=ft.Icons.LOGIN,
        width=100,
        on_click=login_click,
    )

    page.add(
        ft.SafeArea(
            ft.Container(
                ft.Column(
                    [
                        login_title,
                        ft.Container(
                            ft.Column([username, password], spacing=20),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            login_button,
                            alignment=ft.alignment.top_right,
                            margin=ft.margin.only(0, 20, 40, 0),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )


ft.app(target=main)
