using FluentValidation;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Login
{
    public class LoginCommandValidator : AbstractValidator<LoginCommandRequest>
    {
        public LoginCommandValidator()
        {
            RuleFor(x => x.Email)
                .NotEmpty().WithMessage("Email boş geçilemez")
                .EmailAddress().WithMessage("Email formatına uygun olmalı");

            RuleFor(x => x.Password)
                .NotEmpty().WithMessage("Şifre boş geçilemez")
                .MinimumLength(6).MaximumLength(20).WithMessage("Şifre 6-20 karakter arasında olmalı")
                .Matches(@"[A-Z]").WithMessage("Şifre en az bir büyük harf içermeli")
                .Matches(@"[a-z]").WithMessage("Şifre en az bir küçük harf içermeli")
                .Matches(@"[0-9]").WithMessage("Şifre en az bir rakam içermeli");

        }
    }
}
