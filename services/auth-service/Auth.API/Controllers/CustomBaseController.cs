using Auth.Application.DTOs;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Auth.API.Controllers
{
    [Route("api/v1/[controller]")]
    [ApiController]
    [Authorize]
    public class CustomBaseController : ControllerBase
    {
        protected IMediator Mediator => HttpContext.RequestServices.GetService<IMediator>();

        [NonAction]
        public IActionResult CreateActionResultInstance<T>(CustomResponseDto<T> response)
        {
            // Http 204 (No Content) ise geri boş response döndür.
            if (response.StatusCode == 204)
            {
                return new ObjectResult(null)
                {
                    StatusCode = response.StatusCode,
                };
            }
            // Diğer tüm durumlar için (200, 400, 404, 500) için veriyi ve kodu paketle dön.
            return new ObjectResult(response)
            {
                StatusCode = response.StatusCode,
            };
        }

        [NonAction]
        public IActionResult CreateActionResultInstance(CustomResponseDto response)
        {
            // Http 204 (No Content) ise geri boş response döndür.
            if (response.StatusCode == 204)
            {
                return new ObjectResult(null)
                {
                    StatusCode = response.StatusCode,
                };
            }
            // Diğer tüm durumlar için (200, 400, 404, 500) için veriyi ve kodu paketle dön.
            return new ObjectResult(response)
            {
                StatusCode = response.StatusCode,
            };
        }
    }
}
