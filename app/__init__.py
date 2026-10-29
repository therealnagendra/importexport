from pathlib import Path

from flask import Flask, redirect, render_template, session

from app.db import close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    if test_config:
        app.config.update(test_config)

    app.config['UPLOAD_FOLDER'] = app.config.get('UPLOAD_FOLDER', str(Path(app.root_path).parent / 'uploads'))
    app.config['DATABASE_PATH'] = app.config.get('DATABASE_PATH', str(Path(app.root_path).parent / 'instance' / 'import_export.db'))

    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['DATABASE_PATH']).parent.mkdir(parents=True, exist_ok=True)

    @app.before_request
    def ensure_csrf_token():
        import secrets
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)

    app.teardown_appcontext(close_db)

    @app.context_processor
    def inject_csrf():
        return {'csrf_token': session.get('csrf_token')}

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    @app.route('/')
    def index():
        return redirect('/dashboard')

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.shipments import shipments_bp
    from app.routes.parties import parties_bp
    from app.routes.agents import agents_bp
    from app.routes.documents import documents_bp
    from app.routes.expenses import expenses_bp
    from app.routes.tracking import tracking_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(shipments_bp)
    app.register_blueprint(parties_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        init_db()

    return app
