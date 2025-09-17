from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden, InternalServerError, UnprocessableEntity
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended.exceptions import JWTExtendedException
from app.utils.response import error_response, AppError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e: AppError):
        return e.to_response()

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return error_response('NOT_FOUND', '资源不存在', 404)

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return error_response('BAD_REQUEST', '请求参数错误', 400, str(e))

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(e):
        return error_response('UNAUTHORIZED', '未授权访问', 401)

    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return error_response('FORBIDDEN', '没有权限执行该操作', 403)

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        logger.error(f'Database error: {e}')
        return error_response('DB_ERROR', '数据库操作失败', 500)

    @app.errorhandler(UnprocessableEntity)
    def handle_unprocessable_entity(e):
        logger.error(f'Unprocessable Entity error: {e}')
        return error_response('VALIDATION_ERROR', '请求验证失败，请检查请求数据格式', 422)
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        logger.error(f'JWT error: {e}')
        return error_response('JWT_ERROR', '身份验证失败，请重新登录', 401)
    
    @app.errorhandler(Exception)
    def handle_general_error(e):
        logger.error(f'Unhandled error: {e}', exc_info=True)
        return error_response('INTERNAL_ERROR', '服务器内部错误', 500)

    return app