using Auth.Application.DTOs;
using Auth.Application.Interfaces;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Logout
{
    internal class LogoutCommandHandler : IRequestHandler<LogoutCommandRequest, CustomResponseDto>
    {
        private readonly IRefreshTokenRepository _refreshTokenRepository;
        private readonly ICurrentUserService _currentUserService;
        private readonly IUnitOfWork _unitOfWork;

        public LogoutCommandHandler(IRefreshTokenRepository refreshTokenRepository, IUnitOfWork unitOfWork, ICurrentUserService currentUserService)
        {
            _refreshTokenRepository = refreshTokenRepository;
            _unitOfWork = unitOfWork;
            _currentUserService = currentUserService;
        }

        public async Task<CustomResponseDto> Handle(LogoutCommandRequest request, CancellationToken cancellationToken)
        {
            var tokenEntity = await _refreshTokenRepository.GetRefreshTokenAsync(request.RefreshToken);
            var currentUserId = _currentUserService.UserId;

            if(tokenEntity != null && tokenEntity.UserId.ToString() == currentUserId)
            {
                _refreshTokenRepository.Remove(tokenEntity);
                await _unitOfWork.SaveChangesAsync();
            }
            return CustomResponseDto.Success(200, "Çıkış başarılı");
        }
    }
}
