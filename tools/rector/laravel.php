<?php
use Rector\Config\RectorConfig;
use Rector\Transform\Rector\FuncCall\FuncCallToMethodCallRector;
use Rector\Transform\ValueObject\FuncCallToMethodCall;
use Rector\Transform\Rector\MethodCall\MethodCallRector;
use Rector\Transform\ValueObject\MethodCallRename;

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

    // Règle pour migrer les routes (ex. : Route::get avec middleware)
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'Illuminate\Support\Facades\Route',
                'get',
                'middleware'
            ),
        ]
    );

    // Règle pour migrer les modèles Eloquent (ex. : ajouter timestamps)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                'class (\w+) extends Model',
                'class $1 extends Model { public $timestamps = true; }'
            ),
        ]
    );

    // Règle pour migrer les configurations (ex. : config/app.php)
    $rectorConfig->ruleWithConfiguration(
        FileContentRector::class,
        [
            new StringReplace(
                '\'timezone\' => \'UTC\'',
                '\'timezone\' => env(\'APP_TIMEZONE\', \'UTC\')'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};