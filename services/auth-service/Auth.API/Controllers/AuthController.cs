using Auth.Application.Features.Auth.Commands.ForgotPassword;
using Auth.Application.Features.Auth.Commands.GoogleLogin;
using Auth.Application.Features.Auth.Commands.Login;
using Auth.Application.Features.Auth.Commands.Logout;
using Auth.Application.Features.Auth.Commands.RefreshTokens;
using Auth.Application.Features.Auth.Commands.Register;
using Auth.Application.Features.Auth.Commands.ResetPassword;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace Auth.API.Controllers
{
    [Route("api/v1/[controller]/[action]")]
    [ApiController]
    public class AuthController : CustomBaseController
    {
        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> Register([FromBody] RegisterCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> Login([FromBody] LoginCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> RefreshToken([FromBody] RefreshTokenCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [HttpPost]
        public async Task<IActionResult> Logout([FromBody] LogoutCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> ForgotPassword([FromBody] ForgotPasswordCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> ResetPassword([FromBody] ResetPasswordCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));

        [AllowAnonymous]
        [HttpPost]
        public async Task<IActionResult> GoogleLogin([FromBody] GoogleLoginCommandRequest request)
            => CreateActionResultInstance(await Mediator.Send(request));
    }
}
