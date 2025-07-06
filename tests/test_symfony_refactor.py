import pytest
import os
from app.services.symfony.refactor import symfony_refactor

@pytest.mark.asyncio
async def test_symfony_service_refactor(temp_file, mock_run_tool):
    """Teste la migration des services Symfony."""
    input_code = """<?php
namespace App\Service;
use Psr\Log\LoggerInterface;
class MyService {
    public function __construct(LoggerInterface $logger) {
        $this->logger = $logger;
    }
}
"""
    expected_code = """<?php
namespace App\Service;
use Psr\Log\LoggerInterface;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
class MyService {
    public function __construct(
        #[Autowire(service: 'logger')]
        private LoggerInterface $logger
    ) {}
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored service", "")
    
    refactored_code, logs = symfony_refactor(temp_file, version="6")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored service" in logs

@pytest.mark.asyncio
async def test_symfony_bundle_refactor(temp_file, mock_run_tool):
    """Teste la migration des bundles Symfony."""
    input_code = """<?php
class Kernel extends HttpKernel {
    public function registerBundles() {
        return [
            new AppBundle(),
        ];
    }
}
"""
    expected_code = """<?php
class Kernel extends HttpKernel {
    public function registerModernBundles() {
        return [
            new AppBundle(),
        ];
    }
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored bundle", "")
    
    refactored_code, logs = symfony_refactor(temp_file, version="6")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored bundle" in logs

@pytest.mark.asyncio
async def test_symfony_route_refactor(temp_file, mock_run_tool):
    """Teste la migration des routes Symfony."""
    input_code = """<?php
use Symfony\Component\Routing\Annotation\Route;
class HomeController {
    /**
     * @Route("/home", name="home")
     */
    public function index() {}
}
"""
    expected_code = """<?php
use Symfony\Component\Routing\Attribute\Route;
class HomeController {
    #[Route('/home', name: 'home')]
    public function index() {}
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored route", "")
    
    refactored_code, logs = symfony_refactor(temp_file, version="6")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored route" in logs

@pytest.mark.asyncio
async def test_symfony_entity_refactor(temp_file, mock_run_tool):
    """Teste la migration des entités Doctrine."""
    input_code = """<?php
use Doctrine\ORM\Mapping as ORM;
/**
 * @ORM\Entity
 */
class User {}
"""
    expected_code = """<?php
use Doctrine\ORM\Mapping\Attribute\Entity;
#[Entity]
class User {}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored entity", "")
    
    refactored_code, logs = symfony_refactor(temp_file, version="6")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored entity" in logs

@pytest.mark.asyncio
async def test_symfony_config_refactor(temp_file, mock_run_tool):
    """Teste la migration des configurations Symfony."""
    input_code = """<?php
return [
    'parameters' => [
        'app.locale' => 'en',
    ],
];
"""
    expected_code = """<?php
return [
    'parameters' => [
        public const APP_LOCALE = 'en';
    ],
];
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored config", "")
    
    refactored_code, logs = symfony_refactor(temp_file, version="6")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored config" in logs