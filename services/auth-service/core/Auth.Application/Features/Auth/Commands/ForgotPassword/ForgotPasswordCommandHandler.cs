using Auth.Application.DTOs;
using Auth.Application.Interfaces;
using Auth.Application.Exceptions;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.ForgotPassword
{
    internal class ForgotPasswordCommandHandler : IRequestHandler<ForgotPasswordCommandRequest, CustomResponseDto>
    {
        private readonly IUserRepository _userRepository;
        private readonly IEmailService _emailService;
        private readonly IUnitOfWork _unitOfWork;

        public ForgotPasswordCommandHandler(IUserRepository userRepository, IEmailService emailService, IUnitOfWork unitOfWork)
        {
            _userRepository = userRepository;
            _emailService = emailService;
            _unitOfWork = unitOfWork;
        }

        public async Task<CustomResponseDto> Handle(ForgotPasswordCommandRequest request, CancellationToken cancellationToken)
        {
            var user = await _userRepository.GetUserByEmailAsync(request.Email);
            if (user == null)
                throw new NotFoundException("Verilen maile kayıtlı kullanıcı bulunamadı.");

            var resetToken = Guid.NewGuid().ToString("N").Substring(0, 6);
            int expiryMinutes = 15;

            user.ResetToken = resetToken;
            user.PasswordResetTokenExpiry = DateTime.UtcNow.AddMinutes(expiryMinutes);

            _userRepository.Update(user);
            await _unitOfWork.SaveChangesAsync();

            return CustomResponseDto.Success(200, "ResetToken oluşturuldu");
        }
    }
}
