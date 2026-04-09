<?php

namespace App\Filament\Resources;

use App\Filament\Resources\TopicResource\Pages;
use App\Models\Unit;
use App\Models\Topic;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Validation\Rules\Unique;

class TopicResource extends Resource
{
    protected static ?string $model = Topic::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Konular';
    protected static ?string $modelLabel = 'Konu';
    protected static ?string $pluralModelLabel = 'Konular';
    protected static ?string $navigationGroup = 'Icerik';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('unit_id')
                    ->label('Unite')
                    ->options(
                        Unit::query()
                            ->orderBy('grade')
                            ->orderBy('unit_no')
                            ->get()
                            ->mapWithKeys(fn (Unit $unit) => [
                                $unit->id => $unit->grade . '. Sinif / ' . $unit->unit_no . '. Unite - ' . $unit->name,
                            ])
                            ->all()
                    )
                    ->searchable()
                    ->required(),
                Forms\Components\TextInput::make('topic_no')
                    ->label('Konu No')
                    ->required()
                    ->numeric()
                    ->minValue(1)
                    ->unique(
                        ignoreRecord: true,
                        modifyRuleUsing: function (Unique $rule, Forms\Get $get): Unique {
                            return $rule
                                ->where('unit_id', (int) ($get('unit_id') ?? 0));
                        }
                    )
                    ->validationMessages([
                        'unique' => 'Bu unite icin ayni konu numarasi zaten var.',
                    ])
                    ->helperText('Ayni unite icinde ayni konu numarasi tekrar edemez.'),
                Forms\Components\TextInput::make('name')
                    ->label('Konu Adi')
                    ->required(),
                Forms\Components\TextInput::make('order')
                    ->label('Liste Sirasi')
                    ->required()
                    ->numeric()
                    ->default(0),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('unit.name')
                    ->label('Unite')
                    ->searchable(),
                Tables\Columns\TextColumn::make('topic_no')
                    ->label('Konu No')
                    ->sortable(),
                Tables\Columns\TextColumn::make('name')
                    ->label('Konu')
                    ->searchable(),
                Tables\Columns\TextColumn::make('order')
                    ->label('Sira')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\ForceDeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListTopics::route('/'),
            'create' => Pages\CreateTopic::route('/create'),
            'view' => Pages\ViewTopic::route('/{record}'),
            'edit' => Pages\EditTopic::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }
}
