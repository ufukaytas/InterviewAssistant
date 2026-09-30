using Auth.Application.Interfaces;
using Auth.Application.Exceptions;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;
using Auth.Domain.Entities;
using Auth.Application.DTOs;

namespace Auth.Application.Features.Auth.Commands.RefreshTokens
{
    internal class RefreshTokenCommandHandler : IRequestHandler<RefreshTokenCommandRequest, CustomResponseDto<RefreshTokenCommandResponse>>
    {
        private readonly IRefreshTokenRepository _refreshTokenRepository;
        private readonly IJwtTokenGenerator _jwtTokenGenerator;
        private readonly IUnitOfWork _unitOfWork;

        public RefreshTokenCommandHandler(IRefreshTokenRepository refreshTokenRepository, IJwtTokenGenerator jwtTokenGenerator, IUnitOfWork unitOfWork)
        {
            _refreshTokenRepository = refreshTokenRepository;
            _jwtTokenGenerator = jwtTokenGenerator;
            _unitOfWork = unitOfWork;
        }

        public async Task<CustomResponseDto<RefreshTokenCommandResponse>> Handle(RefreshTokenCommandRequest request, CancellationToken cancellationToken)
        {
            var existingToken = await _refreshTokenRepository.GetRefreshTokenAsync(request.RefreshToken);
            if (existingToken == null)
                throw new BusinessException("RefreshToken bulunamadı");

            if (existingToken.IsExpired)
                throw new BusinessException("RefreshToken süresi doldu");

            if (!existingToken.IsActiveToken)
                throw new BusinessException("RefreshToken aktif değil");

            existingToken.RevokedDate = DateTime.UtcNow;
            existingToken.IsActive = false;

            var newTokenDto = _jwtTokenGenerator.GenerateAccessToken(existingToken.User);

            var newRefreshToken = new RefreshToken
            {
                UserId = existingToken.UserId,
                Token = newTokenDto.RefreshToken,
                AccessToken = newTokenDto.AccessToken,
                ExpiresDate = newTokenDto.AccessTokenExpiration.AddDays(7)
            };

            _refreshTokenRepository.Update(existingToken);
            await _refreshTokenRepository.AddAsync(newRefreshToken);
            await _unitOfWork.SaveChangesAsync();

            var responseData = new RefreshTokenCommandResponse
            {
                AccessToken = newTokenDto.AccessToken,
                AccessTokenExpiration = newTokenDto.AccessTokenExpiration,
                RefreshToken = newTokenDto.RefreshToken
            };

            return CustomResponseDto<RefreshTokenCommandResponse>.Success(200, responseData, "Oturum yenilendi");
        }
    }
}
