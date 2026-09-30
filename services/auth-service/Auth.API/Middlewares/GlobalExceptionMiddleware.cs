using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using Auth.Application.Exceptions;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;

namespace Auth.API.Middlewares
{
    public class GlobalExceptionMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<GlobalExceptionMiddleware> _logger;

        public GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                await _next(context);
            }
            catch (Exception ex)
            {
                // Önceki konfigürasyonumuza uygun olarak önce "sub", yoksa "NameIdentifier" arıyoruz
                var userIdentityfier = context.User.Identity?.IsAuthenticated == true
                    ? (context.User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value ?? context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value)
                    : "Anonim";

                await HandleExceptionAsync(context, ex);
            }
        }

        private static async Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            int statusCode = StatusCodes.Status500InternalServerError;
            string title = "Sunucu Hatası";

            var problemDetails = new ProblemDetails
            {
                Instance = context.Request.Path
            };

            switch (exception)
            {
                // Uygulama seviyesi özel hatalarımız
                case ValidationException validationException:
                    statusCode = StatusCodes.Status400BadRequest;
                    title = "Doğrulama Hatası";
                    problemDetails.Extensions.Add("errors", validationException.Errors);
                    break;

                case BusinessException:
                    statusCode = StatusCodes.Status400BadRequest;
                    title = "İş Kuralı İhlali"; 
                    break;

                case NotFoundException: 
                    statusCode = StatusCodes.Status404NotFound;
                    title = "Kaynak Bulunamadı";
                    break;

                case AuthenticationException: 
                    statusCode = StatusCodes.Status401Unauthorized;
                    title = "Giriş Başarısız";
                    break;

                case InvalidOperationException:
                    statusCode = StatusCodes.Status409Conflict;
                    title = "Geçersiz İşlem";
                    break;

                case UnauthorizedAccessException:
                    statusCode = StatusCodes.Status401Unauthorized;
                    title = "Yetkisiz İşlem";
                    break;
            }

            context.Response.ContentType = "application/json";
            context.Response.StatusCode = statusCode;

            problemDetails.Status = statusCode;
            problemDetails.Title = title;
            problemDetails.Detail = exception.Message;

            var jsonResponse = JsonSerializer.Serialize(problemDetails);
            await context.Response.WriteAsync(jsonResponse);
        }
    }
}