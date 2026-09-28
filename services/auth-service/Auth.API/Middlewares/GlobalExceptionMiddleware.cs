using System.Net;
using System.Text.Json;
using Auth.Application.Exceptions;

namespace Auth.API.Middlewares
{
    public class GlobalExceptionMiddleware
    {
        private readonly RequestDelegate _next;

        public GlobalExceptionMiddleware(RequestDelegate next)
        {
            _next = next;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                // İsteği bir sonraki aşamaya (Controller'a vb.) ilet
                await _next(context);
            }
            catch (Exception ex)
            {
                // Hata patlarsa havada yakala ve formatla
                await HandleExceptionAsync(context, ex);
            }
        }

        private static Task HandleExceptionAsync(HttpContext context, Exception exception)
        {
            context.Response.ContentType = "application/json";

            // Gelen hatanın tipine göre farklı HTTP statü kodları dönebiliriz
            return exception switch
            {
                ValidationException validationEx => HandleValidationException(context, validationEx),
                _ => HandleDefaultException(context, exception)
            };
        }

        private static Task HandleValidationException(HttpContext context, ValidationException exception)
        {
            context.Response.StatusCode = (int)HttpStatusCode.BadRequest; // 400

            // Kullanıcıya dönecek JSON formatını ayarlıyoruz
            var result = JsonSerializer.Serialize(new
            {
                Title = "Doğrulama Hatası (Validation Error)",
                Status = context.Response.StatusCode,
                Errors = exception.Errors // ValidationException içinden gelen hata listesi
            });

            return context.Response.WriteAsync(result);
        }

        private static Task HandleDefaultException(HttpContext context, Exception exception)
        {

            Console.WriteLine("---- BEKLENMEYEN HATA YAKALANDI ----");
            Console.WriteLine(exception.ToString());
            Console.WriteLine("------------------------------------");


            context.Response.StatusCode = (int)HttpStatusCode.InternalServerError; // 500
            var result = JsonSerializer.Serialize(new { error = "Sunucu tarafında beklenmeyen bir hata oluştu." });
            return context.Response.WriteAsync(result);
        }
    }
}
