<?php
use Rector\Config\RectorConfig;
use Rector\Transform\Rector\FuncCall\FuncCallToMethodCallRector;
use Rector\Transform\ValueObject\FuncCallToMethodCall;

return static function (RectorConfig $rectorConfig): void {
    // Règles pour migrer Laravel vers une version récente (ex. : 8+)
    $rectorConfig->sets([\Rector\Laravel\Set\LaravelSetList::LARAVEL_80]);

    // Règle pour migrer les helpers (ex. : config() vers Config::get())
    $rectorConfig->ruleWithConfiguration(
        FuncCallToMethodCallRector::class,
        [
            new FuncCallToMethodCall(
                'config',
                'Illuminate\Support\Facades\Config',
                'get'
            ),
        ]
    );

    // Règle pour migrer les sessions (ex. : Session::put vers session()->put)
    $rectorConfig->ruleWithConfiguration(
        FuncCallToMethodCallRector::class,
        [
            new FuncCallToMethodCall(
                'Session::put',
                'Illuminate\Support\Facades\Session',
                'put'
            ),
            new FuncCallToMethodCall(
                'Session::get',
                'Illuminate\Support\Facades\Session',
                'get'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};