using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Login
{
    public class LoginCommandRequest : IRequest<CustomResponseDto<LoginCommandResponse>>
    {
        public string Email { get; set; } = null!;
        public string Password { get; set; } = null!;
    }
}
