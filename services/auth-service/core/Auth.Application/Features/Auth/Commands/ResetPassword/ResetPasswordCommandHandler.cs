using Auth.Application.DTOs;
using Auth.Application.Interfaces;
using Auth.Application.Exceptions;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.ResetPassword
{
    internal class ResetPasswordCommandHandler : IRequestHandler<ResetPasswordCommandRequest, CustomResponseDto>
    {
        private readonly IUserRepository _userRepository;
        private readonly IPasswordHasher _passwordHasher;
        private readonly IUnitOfWork _unitOfWork;

        public ResetPasswordCommandHandler(IUserRepository userRepository, IUnitOfWork unitOfWork, IPasswordHasher passwordHasher)
        {
            _userRepository = userRepository;
            _unitOfWork = unitOfWork;
            _passwordHasher = passwordHasher;
        }

        public async Task<CustomResponseDto> Handle(ResetPasswordCommandRequest request, CancellationToken cancellationToken)
        {
            var user = await _userRepository.GetUserByEmailAsync(request.Email);
            if (user == null)
                throw new NotFoundException("Kayıtlı mail bulunamadı");

            if (user.ResetToken != request.Token)
                throw new BusinessException("Girdiğiniz doğrulama kodu hatalı");

            if (DateTime.UtcNow > user.PasswordResetTokenExpiry)
                throw new BusinessException("Doğrulama kodun süresi doldu");

            user.PasswordHash = _passwordHasher.Hash(request.NewPassword);

            //Güvenlik (kullanılan kodun tekrar kullanılmaması için)
            user.ResetToken = null;
            user.PasswordResetTokenExpiry = null;

            _userRepository.Update(user);
            await _unitOfWork.SaveChangesAsync();

            return CustomResponseDto.Success(200, "Yeni şifre başarıyla oluşturuldu");
        }
    }
}
