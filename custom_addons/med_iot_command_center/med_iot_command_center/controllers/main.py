from odoo import http
from odoo.http import request


class MedIoTAuthController(http.Controller):

    @http.route(['/mediot', '/mediot/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_landing(self, **kwargs):
        return request.render('med_iot_command_center.med_landing_page', {})

    @http.route(['/mediot/login', '/mediot/login/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_login_page(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "login": kwargs.get("login", ""),
            "redirect": "/mediot/post_login",
        }
        return request.render('med_iot_command_center.med_login_page', values)

    @http.route(['/mediot/post_login'], type='http', auth='user', website=False, sitemap=False)
    def mediot_post_login(self, **kwargs):
        user = request.env.user

        if user.has_group('med_iot_command_center.group_med_senior_doctor'):
            action = request.env.ref('med_iot_command_center.action_med_dashboard').sudo()
            menu = request.env.ref('med_iot_command_center.menu_med_dashboard').sudo()
            return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

        if user.has_group('med_iot_command_center.group_med_admin'):
            action = request.env.ref('med_iot_command_center.action_med_dashboard').sudo()
            menu = request.env.ref('med_iot_command_center.menu_med_dashboard').sudo()
            return request.redirect(f'/web#action={action.id}&menu_id={menu.id}')

        return request.redirect('/web')

    @http.route(['/mediot/signup', '/mediot/signup/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_signup_page(self, **kwargs):
        values = {
            "error": kwargs.get("error"),
            "success": kwargs.get("success"),
            "form_data": kwargs,
        }
        return request.render('med_iot_command_center.med_signup_page', values)

    @http.route(
        ['/mediot/signup/submit'],
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True,
        sitemap=False
    )
    def mediot_signup_submit(self, **post):
        Users = request.env['res.users'].sudo()

        email = (post.get('email') or '').strip().lower()
        password = (post.get('password') or '').strip()
        first_name = (post.get('first_name') or '').strip()
        last_name = (post.get('last_name') or '').strip()

        if not email:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Email is required.",
                "form_data": post,
            })

        if not password:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "Password is required.",
                "form_data": post,
            })

        if Users.search_count([('login', '=', email)]) > 0:
            return request.render('med_iot_command_center.med_signup_page', {
                "error": "An account with this email already exists.",
                "form_data": post,
            })

        doctor_group = request.env.ref('med_iot_command_center.group_med_senior_doctor').sudo()
        internal_user_group = request.env.ref('base.group_user').sudo()

        new_user = Users.create({
            'name': f"{first_name} {last_name}".strip() or email,
            'login': email,
            'email': email,
            'password': password,
            'group_ids': [(6, 0, [internal_user_group.id, doctor_group.id])],
        })

        if new_user.partner_id:
            new_user.partner_id.sudo().write({
                'phone': post.get('phone', ''),
                'city': post.get('city', ''),
            })

        return request.render('med_iot_command_center.med_signup_page', {
            "success": "Your account has been created successfully. You can sign in now.",
            "form_data": {},
        })

    @http.route(['/mediot/reset', '/mediot/reset/'], type='http', auth='public', website=True, sitemap=False)
    def mediot_reset_redirect(self, **kwargs):
        return request.redirect('/web/reset_password')

    @http.route(['/mediot/logout', '/mediot/logout/'], type='http', auth='user', website=True, sitemap=False)
    def mediot_logout(self, **kwargs):
        request.session.logout(keep_db=False)
        return request.redirect('/mediot/login')