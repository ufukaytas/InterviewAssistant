using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.ForgotPassword
{
    public class ForgotPasswordCommandRequest : IRequest<CustomResponseDto>
    {
        public string Email { get; set; } = null!;
    }
}
