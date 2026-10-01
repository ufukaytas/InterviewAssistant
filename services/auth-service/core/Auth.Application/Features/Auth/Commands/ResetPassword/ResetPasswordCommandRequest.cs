using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.ResetPassword
{
    public class ResetPasswordCommandRequest : IRequest<CustomResponseDto>
    {
        public string Email { get; set; } = null!;
        public string Token { get; set; } = null!;
        public string NewPassword { get; set; } = null!;
    }
}
